"""
Тесты приложения users.

Проверяются расширенная модель пользователя, регистрация, вход и выход
через сессию, доступ к профилю и его обновление.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserModelTests(TestCase):
    """Дополнительные поля и производные свойства модели пользователя."""

    def test_display_name_prefers_full_name(self):
        user = User.objects.create_user(
            username="svetlakova",
            email="s@example.com",
            password="pass12345",
            first_name="Софья",
            last_name="Светлакова",
        )
        self.assertEqual(user.display_name, "Софья Светлакова")

    def test_display_name_falls_back_to_username(self):
        user = User.objects.create_user(
            username="traveller", email="t@example.com", password="pass12345"
        )
        self.assertEqual(user.display_name, "traveller")

    def test_role_reflects_staff_flag(self):
        user = User.objects.create_user(
            username="user", email="u@example.com", password="pass12345"
        )
        admin = User.objects.create_user(
            username="admin", email="a@example.com", password="pass12345", is_staff=True
        )
        self.assertEqual(user.role, "Пользователь")
        self.assertEqual(admin.role, "Администратор")

    def test_profile_fields_are_optional(self):
        user = User.objects.create_user(
            username="blank", email="b@example.com", password="pass12345"
        )
        self.assertEqual(user.bio, "")
        self.assertEqual(user.phone, "")
        self.assertFalse(user.avatar)


class RegistrationTests(TestCase):
    """Регистрация нового пользователя."""

    def test_page_available_to_guest(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")

    def test_registration_creates_user_and_opens_session(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "newcomer",
                "email": "newcomer@example.com",
                "password1": "Traveller2026",
                "password2": "Traveller2026",
            },
        )
        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertTrue(User.objects.filter(username="newcomer").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(
            username="first", email="taken@example.com", password="pass12345"
        )
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "second",
                "email": "taken@example.com",
                "password1": "Traveller2026",
                "password2": "Traveller2026",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="second").exists())

    def test_mismatched_passwords_rejected(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "careless",
                "email": "careless@example.com",
                "password1": "Traveller2026",
                "password2": "Traveller2027",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="careless").exists())

    def test_authenticated_user_redirected_away(self):
        user = User.objects.create_user(
            username="already", email="al@example.com", password="pass12345"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("users:register"))
        self.assertRedirects(response, reverse("tours:tour_list"))


class SessionAuthTests(TestCase):
    """Вход и выход через сессионную аутентификацию."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="manager", email="m@example.com", password="travel2026"
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "manager", "password": "travel2026"},
        )
        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_keeps_session_closed(self):
        response = self.client.post(
            reverse("users:login"),
            {"username": "manager", "password": "wrong-password"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_closes_session(self):
        self.client.force_login(self.user)
        self.assertIn("_auth_user_id", self.client.session)

        response = self.client.get(reverse("users:logout"))
        self.assertRedirects(response, reverse("tours:tour_list"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    """Доступ к профилю и обновление личных данных."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="traveller", email="t@example.com", password="pass12345"
        )

    def test_guest_redirected_to_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_profile_shows_counters(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["tours_total"], 0)
        self.assertEqual(response.context["favorites_total"], 0)
        self.assertEqual(response.context["reviews_total"], 0)

    def test_profile_update_saves_fields(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Иван",
                "last_name": "Петров",
                "email": "ivan@example.com",
                "phone": "+7 (900) 000-00-00",
                "bio": "Люблю горные маршруты.",
            },
        )
        self.assertRedirects(response, reverse("users:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Иван")
        self.assertEqual(self.user.email, "ivan@example.com")
        self.assertEqual(self.user.bio, "Люблю горные маршруты.")
