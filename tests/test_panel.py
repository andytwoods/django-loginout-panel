from debug_toolbar.toolbar import DebugToolbar
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase
from django.urls import reverse
from django.utils.safestring import SafeString

import loginout_panel
from loginout_panel import LoginOutPanel


def _panel_for(request):
    """Build a real DebugToolbar and return our panel instance."""
    toolbar = DebugToolbar(request, lambda r: HttpResponse())
    return toolbar.get_panel_by_id("LoginOutPanel")


class PanelRegistrationTests(SimpleTestCase):
    def test_exposed_at_dotted_path_used_in_settings(self):
        # DEBUG_TOOLBAR_PANELS references "loginout_panel.LoginOutPanel".
        self.assertIs(loginout_panel.LoginOutPanel, LoginOutPanel)

    def test_get_urls_defines_login_and_logout(self):
        names = {u.name for u in LoginOutPanel.get_urls()}
        self.assertEqual(names, {"loginout_login", "loginout_logout"})

    def test_urls_reverse_under_djdt_namespace(self):
        self.assertTrue(reverse("djdt:loginout_login").endswith("/loginout/login/"))
        self.assertTrue(reverse("djdt:loginout_logout").endswith("/loginout/logout/"))


class NavSubtitleTests(SimpleTestCase):
    def test_template_has_both_links_and_click_handler(self):
        html = render_to_string("loginout_panel/nav_subtitle.html")
        self.assertIn(reverse("djdt:loginout_login"), html)
        self.assertIn(reverse("djdt:loginout_logout"), html)
        self.assertIn("loginoutPanelCall", html)

    def test_nav_subtitle_uses_no_anchors(self):
        # The toolbar wraps nav_subtitle in a <small> inside the panel-button
        # <a>. Anchors here would be invalid nested <a>, which the browser hoists
        # out of the button and misaligns. The controls must be <span>s instead.
        html = render_to_string("loginout_panel/nav_subtitle.html")
        self.assertNotIn("<a ", html)
        self.assertIn('data-loginout-url', html)

    def test_nav_subtitle_wires_button_toggle(self):
        # Clicking the button (not the title text / subtitle links) toggles auth,
        # so the subtitle must expose the auth state and both endpoints and bind
        # the capture-phase handler.
        html = render_to_string(
            "loginout_panel/nav_subtitle.html", {"is_authenticated": True}
        )
        self.assertIn("window.loginoutPanelAuthed = true", html)
        self.assertIn(reverse("djdt:loginout_login"), html)
        self.assertIn(reverse("djdt:loginout_logout"), html)
        self.assertIn("loginoutPanelBound", html)


class NavTitleTests(SimpleTestCase):
    def test_title_wrapped_in_detectable_span(self):
        # The title text must be wrapped so a click on it can be told apart from
        # a click elsewhere on the panel button.
        panel = _panel_for(RequestFactory().get("/"))
        self.assertIn('class="djLoginOutTitle"', panel.nav_title)
        self.assertIn("Login / out", panel.nav_title)

    def test_panel_property_returns_safe_html(self):
        panel = _panel_for(RequestFactory().get("/"))
        subtitle = panel.nav_subtitle
        self.assertIsInstance(subtitle, SafeString)
        self.assertIn(reverse("djdt:loginout_login"), subtitle)

    def test_panel_property_embeds_csrf_token(self):
        # The token is rendered server-side (not read from the cookie) so the
        # POST works even when CSRF_COOKIE_HTTPONLY / CSRF_USE_SESSIONS is set.
        # get_token() returns a freshly masked value each call, so assert a
        # non-empty token is embedded rather than matching an exact string.
        import re

        panel = _panel_for(RequestFactory().get("/"))
        subtitle = panel.nav_subtitle
        match = re.search(r'window\.loginoutPanelCsrf = "([^"]*)"', subtitle)
        self.assertIsNotNone(match)
        self.assertGreater(len(match.group(1)), 0)


class GenerateStatsTests(SimpleTestCase):
    def _stats_for(self, user):
        request = RequestFactory().get("/")
        request.user = user
        panel = _panel_for(request)
        panel.generate_stats(request, HttpResponse())
        return panel.get_stats()

    def test_anonymous_user(self):
        stats = self._stats_for(AnonymousUser())
        self.assertFalse(stats["is_authenticated"])
        self.assertEqual(stats["username"], "tester")  # from LOGINOUT_USERNAME

    def test_no_user_on_request(self):
        # A request without .user must not blow up generate_stats.
        request = RequestFactory().get("/")
        panel = _panel_for(request)
        panel.generate_stats(request, HttpResponse())
        stats = panel.get_stats()
        self.assertFalse(stats["is_authenticated"])
        self.assertEqual(stats["current_user"], "")


class PanelBodyTemplateTests(SimpleTestCase):
    def test_shows_logged_in_user(self):
        html = render_to_string(
            "loginout_panel/panel.html",
            {"is_authenticated": True, "username": "tester", "current_user": "tester"},
        )
        self.assertIn("logged in as", html)
        self.assertIn("tester", html)

    def test_shows_not_logged_in(self):
        html = render_to_string(
            "loginout_panel/panel.html",
            {"is_authenticated": False, "username": "tester", "current_user": ""},
        )
        self.assertIn("not logged in", html)
