from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="manager", email="manager@mail.ru", password="travel2026"
        )

    def test_register(self):
        response = self.client.post(reverse("users:register"), {
            "username": "newuser",
            "email": "new@mail.ru",
            "password1": "Travel2026test",
            "password2": "Travel2026test",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("_auth_user_id", self.client.session)

    def test_register_with_same_email(self):
        response = self.client.post(reverse("users:register"), {
            "username": "second",
            "email": "manager@mail.ru",
            "password1": "Travel2026test",
            "password2": "Travel2026test",
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="second").exists())

    def test_login(self):
        response = self.client.post(reverse("users:login"), {
            "username": "manager",
            "password": "travel2026",
        })
        self.assertEqual(response.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_wrong_password(self):
        self.client.post(reverse("users:login"), {
            "username": "manager",
            "password": "wrong",
        })
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout(self):
        self.client.login(username="manager", password="travel2026")
        self.client.get(reverse("users:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_profile_needs_login(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        self.client.login(username="manager", password="travel2026")
        response = self.client.post(reverse("users:profile"), {
            "first_name": "Софья",
            "last_name": "Светлакова",
            "email": "sofia@mail.ru",
            "phone": "+79001234567",
            "bio": "Люблю горные маршруты.",
        })
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Софья")
        self.assertEqual(self.user.email, "sofia@mail.ru")
