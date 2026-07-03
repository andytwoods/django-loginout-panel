from debug_toolbar.panels import Panel
from django.conf import settings
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import views


class LoginOutPanel(Panel):
    """A Django Debug Toolbar panel that logs a configured user in or out.

    The login/logout endpoints are POST-only, CSRF-protected, and guarded by
    both the toolbar's SHOW_TOOLBAR_CALLBACK (via ``require_show_toolbar``) and
    an explicit ``settings.DEBUG`` check, so they 404 outside development.

    Configuration (project settings):
        LOGINOUT_USERNAME  – username of the account to log in as (required).
        LOGINOUT_SERVER    – optional client IP allowed to use the panel. When
                             set, requests from any other IP get a 404.
        LOGINOUT_TRUST_XFF – trust the ``X-Forwarded-For`` header when resolving
                             the client IP for LOGINOUT_SERVER. Only enable this
                             behind a reverse proxy that overwrites the header;
                             otherwise it is client-spoofable. Defaults to False.
    """

    title = _("Login / out")

    template = "loginout_panel/panel.html"

    @property
    def nav_title(self):
        # Wrap the label so the panel's JS can tell a click on the title text
        # (open the panel body) apart from a click elsewhere on the button
        # (toggle login/logout).
        return format_html(
            '<span class="djLoginOutTitle">{}</span>', _("Login / out")
        )

    @property
    def nav_subtitle(self):
        # Render the CSRF token into the template so the panel's JS can send it
        # in the X-CSRFToken header. Reading it from the ``csrftoken`` cookie in
        # JS (the obvious approach) breaks when the project sets
        # CSRF_COOKIE_HTTPONLY=True (cookie unreadable from JS) or
        # CSRF_USE_SESSIONS=True (no CSRF cookie at all); get_token works in
        # every case. ``is_authenticated`` lets the button-level click pick the
        # login or logout endpoint when toggling.
        request = self.toolbar.request
        token = get_token(request)
        user = getattr(request, "user", None)
        is_authenticated = bool(user is not None and user.is_authenticated)
        return mark_safe(
            render_to_string(
                "loginout_panel/nav_subtitle.html",
                {"csrf_token": token, "is_authenticated": is_authenticated},
            )
        )

    @classmethod
    def get_urls(cls):
        return [
            path("loginout/login/", views.login_view, name="loginout_login"),
            path("loginout/logout/", views.logout_view, name="loginout_logout"),
        ]

    def generate_stats(self, request, response):
        # Ensure the CSRF cookie is set so the panel's POST calls can send the
        # token back (the endpoints are csrf_protect'd).
        get_token(request)
        user = getattr(request, "user", None)
        self.record_stats(
            {
                "username": getattr(settings, "LOGINOUT_USERNAME", None),
                "is_authenticated": bool(user is not None and user.is_authenticated),
                "current_user": str(user) if user is not None else "",
            }
        )
