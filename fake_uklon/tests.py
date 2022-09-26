from django.contrib.auth.models import User
from django.test import Client, TestCase


class UserAusenticateTest(TestCase):
    def setUp(self):
        user = User.objects.create_user("TestUserName", "test@user.mail", "My_password")
        user.save()
        self.c = Client()

    def test_user_authenticate_ok(self):
        """input correct login and password"""
        response = self.c.post(
            "/fake_uklon/login/", {"login": "TestUserName", "password": "My_password"}
        )
        self.assertEqual(response.status_code, 200, "error")
        content = str(response.content)
        self.assertIn("Hello, ", content, "error logining")

    def test_user_authenticate_err(self):
        """input wrong password"""
        response = self.c.post(
            "/fake_uklon/login/",
            {"login": "TestUserName", "password": "My_wrong_password"},
        )
        self.assertEqual(response.status_code, 200, "error")
        content = str(response.content)
        self.assertIn("Wrong login or password", content, "error logining")
