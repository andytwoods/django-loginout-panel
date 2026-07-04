"""Minimal settings for the django-loginout-panel demo.

This is a throwaway development project whose only purpose is to show the panel
in action (and record the README GIF). Never model a production config on it.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "demo-only-not-a-secret"

# The panel is deliberately dev-only; it 404s unless DEBUG is on.
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# django-debug-toolbar shows itself only for these client IPs.
INTERNAL_IPS = ["127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "loginout_panel",
    "home",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "demo_site.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    },
}

STATIC_URL = "static/"

USE_TZ = True

# --- django-loginout-panel configuration -------------------------------------

DEBUG_TOOLBAR_PANELS = [
    "loginout_panel.panel.LoginOutPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "debug_toolbar.panels.sql.SQLPanel",
]

# The account the panel logs in as. `manage.py seed` creates it.
LOGINOUT_USERNAME = "demo"
