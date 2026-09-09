"""Формы приложения tours."""

from django import forms

from .models import Review, Tour

BOOTSTRAP_INPUT = {"class": "form-control"}
BOOTSTRAP_SELECT = {"class": "form-select"}


class TourForm(forms.ModelForm):
    """Форма создания и редактирования туристического предложения."""

    class Meta:
        model = Tour
        fields = (
            "title",
            "country",
            "description",
            "price",
            "duration_days",
            "photo",
            "is_published",
        )
        widgets = {
            "title": forms.TextInput(
                {**BOOTSTRAP_INPUT, "placeholder": "Например: Осенний Токио"}
            ),
            "country": forms.Select(BOOTSTRAP_SELECT),
            "description": forms.Textarea({**BOOTSTRAP_INPUT, "rows": 8}),
            "price": forms.NumberInput({**BOOTSTRAP_INPUT, "min": 0, "step": "0.01"}),
            "duration_days": forms.NumberInput({**BOOTSTRAP_INPUT, "min": 1}),
            "photo": forms.ClearableFileInput({"class": "form-control"}),
            "is_published": forms.CheckboxInput({"class": "form-check-input"}),
        }

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if len(title) < 5:
            raise forms.ValidationError("Название должно содержать не менее 5 символов.")
        return title

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Стоимость тура должна быть больше нуля.")
        return price


class ReviewForm(forms.ModelForm):
    """Форма отзыва о туре."""

    class Meta:
        model = Review
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                {
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Расскажите о впечатлениях от тура",
                }
            ),
        }
        labels = {"text": ""}

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 10:
            raise forms.ValidationError("Отзыв должен содержать не менее 10 символов.")
        return text
