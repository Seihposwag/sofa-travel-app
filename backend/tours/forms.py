from django import forms

from .models import Review, Tour


class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = ["title", "country", "description", "price", "duration_days", "photo"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 8}),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "duration_days": forms.NumberInput(attrs={"class": "form-control"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_price(self):
        price = self.cleaned_data["price"]
        if price <= 0:
            raise forms.ValidationError("Цена должна быть больше нуля.")
        return price


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["text"]
        labels = {"text": ""}
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ваш отзыв о туре",
            }),
        }

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 10:
            raise forms.ValidationError("Отзыв должен быть не короче 10 символов.")
        return text
