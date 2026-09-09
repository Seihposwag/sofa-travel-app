import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Country, Review, Tour

User = get_user_model()


class TourTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(
            username="author", email="author@mail.ru", password="test12345"
        )
        self.other = User.objects.create_user(
            username="other", email="other@mail.ru", password="test12345"
        )
        self.country = Country.objects.create(title="Япония")

        # 8 туров, чтобы проверить пагинацию по 6
        for i in range(8):
            Tour.objects.create(
                title="Тур %d" % i,
                description="Океан, вулканы и рисовые террасы",
                price=100000,
                country=self.country,
                author=self.author,
            )

        self.tour = Tour.objects.first()

    def test_catalog_opens(self):
        response = self.client.get(reverse("tours:tour_list"))
        self.assertEqual(response.status_code, 200)

    def test_pagination(self):
        response = self.client.get(reverse("tours:tour_list"))
        page = response.context["page_obj"]
        self.assertEqual(page.paginator.num_pages, 2)
        self.assertEqual(len(page.object_list), 6)

    def test_search(self):
        response = self.client.get(reverse("tours:tour_list"), {"q": "вулканы"})
        self.assertEqual(response.context["page_obj"].paginator.count, 8)

        response = self.client.get(reverse("tours:tour_list"), {"q": "антарктида"})
        self.assertEqual(response.context["page_obj"].paginator.count, 0)

    def test_filter_by_country(self):
        italy = Country.objects.create(title="Италия")
        Tour.objects.create(
            title="Рим", description="Колизей", price=87000,
            country=italy, author=self.author,
        )
        response = self.client.get(reverse("tours:tours_by_country", args=[italy.pk]))
        self.assertEqual(response.context["page_obj"].paginator.count, 1)

    def test_tour_page_opens(self):
        response = self.client.get(self.tour.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_guest_cannot_create(self):
        response = self.client.get(reverse("tours:tour_create"))
        self.assertEqual(response.status_code, 302)

    def test_create_tour(self):
        self.client.login(username="author", password="test12345")
        response = self.client.post(reverse("tours:tour_create"), {
            "title": "Мальдивы",
            "country": self.country.pk,
            "description": "Бунгало над водой",
            "price": "265000",
            "duration_days": 8,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Tour.objects.get(title="Мальдивы").author, self.author)

    def test_price_must_be_positive(self):
        self.client.login(username="author", password="test12345")
        response = self.client.post(reverse("tours:tour_create"), {
            "title": "Бесплатный тур",
            "country": self.country.pk,
            "description": "Описание",
            "price": "0",
            "duration_days": 5,
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tour.objects.filter(title="Бесплатный тур").exists())

    def test_cannot_edit_other_tour(self):
        self.client.login(username="other", password="test12345")
        self.client.post(reverse("tours:tour_update", args=[self.tour.pk]), {
            "title": "Взломанное название",
            "country": self.country.pk,
            "description": "Описание",
            "price": "1000",
            "duration_days": 3,
        })
        self.tour.refresh_from_db()
        self.assertEqual(self.tour.title, "Тур 7")

    def test_delete_own_tour(self):
        self.client.login(username="author", password="test12345")
        self.client.post(reverse("tours:tour_delete", args=[self.tour.pk]))
        self.assertFalse(Tour.objects.filter(pk=self.tour.pk).exists())


class ReviewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="traveller", email="t@mail.ru", password="test12345"
        )
        self.country = Country.objects.create(title="Италия")
        self.tour = Tour.objects.create(
            title="Рим и Флоренция",
            description="Колизей и Уффици",
            price=87000,
            country=self.country,
            author=self.user,
        )
        self.url = reverse("tours:review_add_ajax", args=[self.tour.pk])

    def test_add_review(self):
        self.client.login(username="traveller", password="test12345")
        response = self.client.post(self.url, {"text": "Хорошая организация поездки"})

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data["ok"])
        self.assertEqual(data["total"], 1)
        self.assertEqual(Review.objects.count(), 1)

    def test_short_review_not_saved(self):
        self.client.login(username="traveller", password="test12345")
        response = self.client.post(self.url, {"text": "Норм"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_guest_cannot_add_review(self):
        response = self.client.post(self.url, {"text": "Отзыв без входа"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 0)
