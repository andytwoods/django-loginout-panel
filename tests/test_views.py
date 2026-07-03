from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


# Django's test runner forces settings.DEBUG = False, but the panel endpoints
# are deliberately dev-only (guarded by both the toolbar callback and an
# explicit DEBUG check). The happy-path suites therefore opt back into
# DEBUG=True to exercise the endpoints as they behave during development.
@override_settings(DEBUG=True)
class LoginLogoutTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw")
        cls.login_url = reverse("djdt:loginout_login")
        cls.logout_url = reverse("djdt:loginout_logout")

    def test_login_authenticates_configured_user(self):
        resp = self.client.post(self.login_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "logged-in")
        self.assertEqual(self.client.session.get(SESSION_KEY), str(self.user.pk))

    def test_logout_clears_the_session(self):
        self.client.post(self.login_url)
        resp = self.client.post(self.logout_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "logged-out")
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_get_is_rejected(self):
        # State-changing endpoints must not respond to GET (login-CSRF guard).
        resp = self.client.get(self.login_url)
        self.assertEqual(resp.status_code, 405)
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(LOGINOUT_USERNAME=None)
    def test_login_without_configured_username_is_400(self):
        resp = self.client.post(self.login_url)
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(LOGINOUT_USERNAME="does-not-exist")
    def test_login_with_unknown_user_is_400(self):
        resp = self.client.post(self.login_url)
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_inactive_user_is_not_logged_in(self):
        self.user.is_active = False
        self.user.save()
        resp = self.client.post(self.login_url)
        self.assertEqual(resp.status_code, 400)
        self.assertNotIn(SESSION_KEY, self.client.session)


class ProductionGuardTests(TestCase):
    """The endpoints must never be reachable outside development."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw")
        cls.login_url = reverse("djdt:loginout_login")

    @override_settings(DEBUG=False)
    def test_login_is_404_when_debug_off(self):
        resp = self.client.post(self.login_url)
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(DEBUG=True, INTERNAL_IPS=[])
    def test_login_is_404_when_toolbar_hidden(self):
        # Even with DEBUG on, SHOW_TOOLBAR_CALLBACK hides the toolbar because
        # the caller is not an internal IP, so require_show_toolbar 404s.
        resp = self.client.post(self.login_url, REMOTE_ADDR="203.0.113.9")
        self.assertEqual(resp.status_code, 404)
        self.assertNotIn(SESSION_KEY, self.client.session)

    @override_settings(DEBUG=True)
    def test_csrf_token_is_required(self):
        enforced = Client(enforce_csrf_checks=True)
        resp = enforced.post(self.login_url)
        self.assertEqual(resp.status_code, 403)
        self.assertNotIn(SESSION_KEY, enforced.session)


@override_settings(
    DEBUG=True,
    LOGINOUT_SERVER="10.0.0.5",
    INTERNAL_IPS=["127.0.0.1", "10.0.0.5"],
)
class LocalServerGuardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw")
        cls.login_url = reverse("djdt:loginout_login")

    def test_request_from_other_ip_is_404(self):
        resp = self.client.post(self.login_url, REMOTE_ADDR="127.0.0.1")
        self.assertEqual(resp.status_code, 404)

    def test_request_from_allowed_ip_passes(self):
        resp = self.client.post(self.login_url, REMOTE_ADDR="10.0.0.5")
        self.assertEqual(resp.status_code, 200)

    def test_x_forwarded_for_is_ignored_by_default(self):
        # Without LOGINOUT_TRUST_XFF, a client-supplied header cannot spoof the
        # allowlisted IP; only REMOTE_ADDR counts.
        resp = self.client.post(
            self.login_url,
            REMOTE_ADDR="10.0.0.5",
            HTTP_X_FORWARDED_FOR="1.2.3.4",
        )
        self.assertEqual(resp.status_code, 200)

    def test_x_forwarded_for_cannot_spoof_allowlist(self):
        resp = self.client.post(
            self.login_url,
            REMOTE_ADDR="127.0.0.1",
            HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.5",
        )
        self.assertEqual(resp.status_code, 404)

    @override_settings(LOGINOUT_TRUST_XFF=True)
    def test_x_forwarded_for_trusted_when_opted_in(self):
        resp = self.client.post(
            self.login_url,
            REMOTE_ADDR="127.0.0.1",
            HTTP_X_FORWARDED_FOR="1.2.3.4, 10.0.0.5",
        )
        self.assertEqual(resp.status_code, 200)
