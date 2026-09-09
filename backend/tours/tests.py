"""
Тесты приложения tours.

Проверяются модели и их связи, публичные представления с пагинацией
и поиском, разграничение прав при редактировании и удаление, а также
AJAX-обработчики отзывов, избранного и подсказок поиска.
"""

import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Country, Favorite, Review, Tour

User = get_user_model()


class CountryModelTests(TestCase):
    """Модель направления: транслитерация адреса и подсчёт предложений."""

    def test_slug_transliterated_from_russian_title(self):
        country = Country.objects.create(title="Япония")
        self.assertEqual(country.slug, "yaponiya")

    def test_absolute_url_uses_slug(self):
        country = Country.objects.create(title="Франция")
        self.assertEqual(country.get_absolute_url(), "/country/franciya/")

    def test_published_tours_count_ignores_drafts(self):
        country = Country.objects.create(title="Италия")
        Tour.objects.create(
            title="Рим и Флоренция",
            description="Описание тура",
            price=Decimal("87000"),
            country=country,
        )
        Tour.objects.create(
            title="Черновик тура",
            description="Описание тура",
            price=Decimal("1000"),
            country=country,
            is_published=False,
        )
        self.assertEqual(country.published_tours_count, 1)


class TourModelTests(TestCase):
    """Модель тура: связи и производные значения."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username="author", email="a@example.com", password="pass12345"
        )
        cls.country = Country.objects.create(title="Турция")
        cls.tour = Tour.objects.create(
            title="Каппадокия и Памуккале",
            description="Описание тура",
            price=Decimal("71000"),
            country=cls.country,
            author=cls.author,
        )

    def test_tour_linked_to_country_and_author(self):
        self.assertEqual(self.tour.country, self.country)
        self.assertEqual(self.tour.author, self.author)
        self.assertIn(self.tour, self.country.tours.all())

    def test_reviews_count_counts_only_active(self):
        Review.objects.create(tour=self.tour, author=self.author, text="Хороший тур")
        Review.objects.create(
            tour=self.tour, author=self.author, text="Скрытый отзыв", is_active=False
        )
        self.assertEqual(self.tour.reviews_count, 1)

    def test_favorite_pair_is_unique(self):
        Favorite.objects.create(user=self.author, tour=self.tour)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.author, tour=self.tour)


class PublicViewTests(TestCase):
    """Публичная часть: каталог, пагинация, поиск, детальный просмотр."""

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(title="Индонезия")
        cls.author = User.objects.create_user(
            username="manager", email="m@example.com", password="pass12345"
        )
        for number in range(8):
            Tour.objects.create(
                title=f"Тур номер {number}",
                description="Океан, вулканы и рисовые террасы",
                price=Decimal("100000"),
                country=cls.country,
                author=cls.author,
            )

    def test_catalog_available_to_guest(self):
        response = self.client.get(reverse("tours:tour_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tours/tour_list.html")

    def test_pagination_splits_catalog_by_six(self):
        response = self.client.get(reverse("tours:tour_list"))
        page = response.context["page_obj"]
        self.assertEqual(page.paginator.num_pages, 2)
        self.assertEqual(len(page.object_list), 6)

    def test_second_page_holds_remaining_tours(self):
        response = self.client.get(reverse("tours:tour_list"), {"page": 2})
        self.assertEqual(len(response.context["page_obj"].object_list), 2)

    def test_search_filters_by_description(self):
        response = self.client.get(reverse("tours:tour_list"), {"q": "вулканы"})
        self.assertEqual(response.context["page_obj"].paginator.count, 8)

    def test_search_without_matches_returns_empty_page(self):
        response = self.client.get(reverse("tours:tour_list"), {"q": "антарктида"})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_tours_by_country_filters_selection(self):
        other = Country.objects.create(title="Мальдивы")
        Tour.objects.create(
            title="Неделя на атолле",
            description="Бунгало над водой",
            price=Decimal("265000"),
            country=other,
            author=self.author,
        )
        response = self.client.get(
            reverse("tours:tours_by_country", kwargs={"slug": other.slug})
        )
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_detail_increments_view_counter(self):
        tour = Tour.objects.first()
        self.client.get(tour.get_absolute_url())
        tour.refresh_from_db()
        self.assertEqual(tour.views, 1)

    def test_draft_hidden_from_guest(self):
        draft = Tour.objects.create(
            title="Скрытый тур",
            description="Описание",
            price=Decimal("1000"),
            country=self.country,
            author=self.author,
            is_published=False,
        )
        response = self.client.get(draft.get_absolute_url())
        self.assertRedirects(response, reverse("tours:tour_list"))


class PermissionTests(TestCase):
    """Разграничение доступа к созданию, изменению и удалению туров."""

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(title="Италия")
        cls.owner = User.objects.create_user(
            username="owner", email="o@example.com", password="pass12345"
        )
        cls.stranger = User.objects.create_user(
            username="stranger", email="s@example.com", password="pass12345"
        )
        cls.admin = User.objects.create_user(
            username="admin", email="ad@example.com", password="pass12345", is_staff=True
        )
        cls.tour = Tour.objects.create(
            title="Амальфитанское побережье",
            description="Позитано, Амальфи и Равелло",
            price=Decimal("112000"),
            country=cls.country,
            author=cls.owner,
        )

    def test_guest_redirected_from_create(self):
        response = self.client.get(reverse("tours:tour_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_owner_can_create_tour(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("tours:tour_create"),
            {
                "title": "Рим и Флоренция",
                "country": self.country.pk,
                "description": "Классический маршрут по двум городам",
                "price": "87000",
                "duration_days": 6,
                "is_published": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Tour.objects.get(title="Рим и Флоренция")
        self.assertEqual(created.author, self.owner)

    def test_short_title_rejected_by_form(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("tours:tour_create"),
            {
                "title": "Рим",
                "country": self.country.pk,
                "description": "Описание",
                "price": "87000",
                "duration_days": 6,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tour.objects.filter(title="Рим").exists())

    def test_stranger_cannot_edit_foreign_tour(self):
        self.client.force_login(self.stranger)
        response = self.client.post(
            reverse("tours:tour_update", kwargs={"pk": self.tour.pk}),
            {
                "title": "Подменённое название",
                "country": self.country.pk,
                "description": "Описание",
                "price": "1000",
                "duration_days": 3,
            },
        )
        self.assertRedirects(response, self.tour.get_absolute_url())
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.title, "Амальфитанское побережье")

    def test_admin_can_edit_any_tour(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse("tours:tour_update", kwargs={"pk": self.tour.pk}),
            {
                "title": "Обновлённое администратором",
                "country": self.country.pk,
                "description": "Описание тура после правки",
                "price": "120000",
                "duration_days": 9,
                "is_published": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.title, "Обновлённое администратором")

    def test_owner_can_delete_own_tour(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("tours:tour_delete", kwargs={"pk": self.tour.pk})
        )
        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertFalse(Tour.objects.filter(pk=self.tour.pk).exists())

    def test_stranger_cannot_delete_foreign_tour(self):
        self.client.force_login(self.stranger)
        self.client.post(reverse("tours:tour_delete", kwargs={"pk": self.tour.pk}))
        self.assertTrue(Tour.objects.filter(pk=self.tour.pk).exists())


class AjaxTests(TestCase):
    """AJAX-обработчики: отзывы, избранное и подсказки поиска."""

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(title="Япония")
        cls.user = User.objects.create_user(
            username="traveller", email="t@example.com", password="pass12345"
        )
        cls.tour = Tour.objects.create(
            title="Осенний Токио и Киото",
            description="Небоскрёбы Синдзюку и клёны Киото",
            price=Decimal("189000"),
            country=cls.country,
            author=cls.user,
        )

    def test_review_added_and_html_returned(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("tours:review_add_ajax", kwargs={"pk": self.tour.pk}),
            {"text": "Отличная организация поездки"},
        )
        self.assertEqual(response.status_code, 200)
        payload = json.loads(response.content)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["total"], 1)
        self.assertIn("Отличная организация поездки", payload["html"])

    def test_short_review_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("tours:review_add_ajax", kwargs={"pk": self.tour.pk}),
            {"text": "Норм"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Review.objects.exists())

    def test_guest_cannot_post_review(self):
        response = self.client.post(
            reverse("tours:review_add_ajax", kwargs={"pk": self.tour.pk}),
            {"text": "Отзыв без авторизации"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.exists())

    def test_favorite_toggles_both_ways(self):
        self.client.force_login(self.user)
        url = reverse("tours:favorite_toggle_ajax", kwargs={"pk": self.tour.pk})

        first = json.loads(self.client.post(url).content)
        self.assertTrue(first["in_favorites"])
        self.assertEqual(Favorite.objects.count(), 1)

        second = json.loads(self.client.post(url).content)
        self.assertFalse(second["in_favorites"])
        self.assertEqual(Favorite.objects.count(), 0)

    def test_search_suggest_requires_two_characters(self):
        response = self.client.get(reverse("tours:search_suggest_ajax"), {"q": "т"})
        self.assertEqual(json.loads(response.content)["results"], [])

    def test_search_suggest_returns_matches(self):
        response = self.client.get(reverse("tours:search_suggest_ajax"), {"q": "Токио"})
        results = json.loads(response.content)["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Осенний Токио и Киото")
        self.assertEqual(results[0]["country"], "Япония")


class FavoritesPageTests(TestCase):
    """Личный список избранного."""

    @classmethod
    def setUpTestData(cls):
        cls.country = Country.objects.create(title="Мальдивы")
        cls.user = User.objects.create_user(
            username="guest", email="g@example.com", password="pass12345"
        )
        cls.tour = Tour.objects.create(
            title="Неделя на атолле",
            description="Бунгало над водой",
            price=Decimal("265000"),
            country=cls.country,
            author=cls.user,
        )

    def test_guest_redirected_to_login(self):
        response = self.client.get(reverse("tours:favorites_list"))
        self.assertEqual(response.status_code, 302)

    def test_favorites_show_only_saved_tours(self):
        self.client.force_login(self.user)
        empty = self.client.get(reverse("tours:favorites_list"))
        self.assertEqual(empty.context["page_obj"].paginator.count, 0)

        Favorite.objects.create(user=self.user, tour=self.tour)
        filled = self.client.get(reverse("tours:favorites_list"))
        self.assertEqual(filled.context["page_obj"].paginator.count, 1)
