from debug_toolbar.panels import Panel
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from . import views


class LoginOutPanel(Panel):
    """A Django Debug Toolbar panel that logs a configured user in or out.

    Configuration (project settings):
        LOGINOUT_USERNAME  – username of the account to log in as (required).
        LOGINOUT_SERVER    – optional client IP allowed to use the panel. When
                             set, requests from any other IP get a 404. When
                             unset, the panel relies on the toolbar's own
                             SHOW_TOOLBAR_CALLBACK (i.e. it is dev-only anyway).
    """

    title = _("Login / out")

    template = "loginout_panel/panel.html"

    @property
    def nav_title(self):
        return _("Login / out")

    @property
    def nav_subtitle(self):
        return mark_safe(render_to_string("loginout_panel/nav_subtitle.html"))

    @classmethod
    def get_urls(cls):
        return [
            path("loginout/login/", views.login_view, name="loginout_login"),
            path("loginout/logout/", views.logout_view, name="loginout_logout"),
        ]

    def generate_stats(self, request, response):
        user = getattr(request, "user", None)
        self.record_stats(
            {
                "username": getattr(settings, "LOGINOUT_USERNAME", None),
                "is_authenticated": bool(user is not None and user.is_authenticated),
                "current_user": str(user) if user is not None else "",
            }
        )
