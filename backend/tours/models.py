"""
Модели предметной области «Бюро путешествий».

Country — модель категории (направление), Tour — основная сущность
(туристическое предложение). Review и Favorite обеспечивают
дополнительный функционал: отзывы и избранное.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse

from .utils import slugify_ru


class Country(models.Model):
    """Направление путешествия. Выступает категорией для предложений."""

    title = models.CharField(
        "Название",
        max_length=150,
        unique=True,
        db_index=True,
    )
    slug = models.SlugField("Идентификатор в адресе", max_length=160, unique=True)
    description = models.TextField("Описание направления", blank=True)
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("tours:tours_by_country", kwargs={"slug": self.slug})

    @property
    def published_tours_count(self):
        return self.tours.filter(is_published=True).count()


class Tour(models.Model):
    """Туристическое предложение — основная публикация бюро."""

    title = models.CharField("Название тура", max_length=200)
    description = models.TextField("Описание")
    price = models.DecimalField("Стоимость, руб.", max_digits=10, decimal_places=2)
    duration_days = models.PositiveSmallIntegerField("Длительность, дней", default=7)
    photo = models.ImageField("Фотография", upload_to="tours/", blank=True, null=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)
    is_published = models.BooleanField("Опубликовано", default=True, db_index=True)
    views = models.PositiveIntegerField("Просмотры", default=0)
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
        indexes = [
            models.Index(fields=["country", "-created_at"], name="idx_tour_country_date"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name="tour_price_non_negative",
            ),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("tours:tour_detail", kwargs={"pk": self.pk})

    @property
    def reviews_count(self):
        return self.reviews.filter(is_active=True).count()


class Review(models.Model):
    """Отзыв пользователя о туре."""

    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Тур",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Автор",
    )
    text = models.TextField("Текст отзыва", max_length=2000)
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    is_active = models.BooleanField("Отображается", default=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв {self.author} о туре «{self.tour}»"


class Favorite(models.Model):
    """Тур, добавленный пользователем в избранное."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Тур",
    )
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tour"],
                name="unique_favorite_user_tour",
            ),
        ]

    def __str__(self):
        return f"{self.user} → {self.tour}"
