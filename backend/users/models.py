"""Модели приложения users: расширенная модель пользователя системы."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    """
    Пользователь системы.

    Наследуется от AbstractUser, поэтому получает username, email, пароль
    в виде хеша, first_name, last_name, is_staff и is_active. Дополнительно
    хранит сведения профиля: биографию, аватар и телефон.
    """

    email = models.EmailField("Электронная почта", unique=True)
    bio = models.TextField("О себе", blank=True)
    avatar = models.ImageField(
        "Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["username"]

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("users:profile")

    @property
    def display_name(self):
        """Имя для показа в интерфейсе: полное имя, иначе логин."""
        full_name = self.get_full_name().strip()
        return full_name or self.username

    @property
    def role(self):
        """Роль пользователя для разграничения доступа."""
        if self.is_staff:
            return "Администратор"
        return "Пользователь"
