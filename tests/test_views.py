from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

User = get_user_model()


class LoginLogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw")
        cls.login_url = reverse("djdt:loginout_login")
        cls.logout_url = reverse("djdt:loginout_logout")

    def test_login_authenticates_configured_user(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "logged-in")
        self.assertEqual(self.client.session.get(SESSION_KEY), str(self.user.pk))

    def test_logout_clears_the_session(self):
        self.client.get(self.login_url)
        resp = self.client.get(self.logout_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "logged-out")
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(LOGINOUT_USERNAME=None)
    def test_login_without_configured_username_is_400(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(LOGINOUT_USERNAME="does-not-exist")
    def test_login_with_unknown_user_is_400(self):
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn(SESSION_KEY, self.client.session)


@override_settings(LOGINOUT_SERVER="10.0.0.5")
class LocalServerGuardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw")
        cls.login_url = reverse("djdt:loginout_login")

    def test_request_from_other_ip_is_404(self):
        resp = self.client.get(self.login_url, REMOTE_ADDR="127.0.0.1")
        self.assertEqual(resp.status_code, 404)

    def test_request_from_allowed_ip_passes(self):
        resp = self.client.get(self.login_url, REMOTE_ADDR="10.0.0.5")
        self.assertEqual(resp.status_code, 200)

    def test_uses_last_x_forwarded_for_hop(self):
        resp = self.client.get(
            self.login_url,
            REMOTE_ADDR="127.0.0.1",
            HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.5",
        )
        self.assertEqual(resp.status_code, 200)
