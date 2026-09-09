from django.conf import settings
from django.db import models
from django.urls import reverse


class Country(models.Model):
    title = models.CharField("Название", max_length=150, unique=True)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:tours_by_country", args=[self.pk])


class Tour(models.Model):
    title = models.CharField("Название", max_length=200)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена, руб.", max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField("Дней", default=7)
    photo = models.ImageField("Фото", upload_to="tours/", blank=True, null=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True, db_index=True)
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="tours",
        verbose_name="Направление",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="tours",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Тур"
        verbose_name_plural = "Туры"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:tour_detail", args=[self.pk])


class Review(models.Model):
    tour = models.ForeignKey(
        Tour, on_delete=models.CASCADE, related_name="reviews", verbose_name="Тур"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    text = models.TextField("Текст")
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.author}"
