"""Формы приложения users: регистрация, вход и редактирование профиля."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User

CONTROL = {"class": "form-control"}


class RegisterForm(UserCreationForm):
    """Регистрация нового пользователя."""

    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        widget=forms.TextInput(CONTROL),
    )
    email = forms.EmailField(label="Электронная почта", widget=forms.EmailInput(CONTROL))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(CONTROL))
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(CONTROL),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с такой почтой уже зарегистрирован.")
        return email


class LoginForm(AuthenticationForm):
    """Вход в систему по логину и паролю."""

    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput(CONTROL))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(CONTROL))


class ProfileUpdateForm(forms.ModelForm):
    """Редактирование личных данных пользователя."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "bio", "avatar")
        widgets = {
            "first_name": forms.TextInput(CONTROL),
            "last_name": forms.TextInput(CONTROL),
            "email": forms.EmailInput(CONTROL),
            "phone": forms.TextInput({**CONTROL, "placeholder": "+7 (000) 000-00-00"}),
            "bio": forms.Textarea({**CONTROL, "rows": 4}),
            "avatar": forms.ClearableFileInput({"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Эта почта занята другим пользователем.")
        return email
