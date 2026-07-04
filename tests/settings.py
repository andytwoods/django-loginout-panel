SECRET_KEY = "NOTASECRET"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}

ALLOWED_HOSTS: list[str] = []
INTERNAL_IPS = ["127.0.0.1"]

# The suite drives the panel/toolbar directly rather than through the
# middleware, so silence the "middleware missing" check.
SILENCED_SYSTEM_CHECKS = ["debug_toolbar.W001"]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "debug_toolbar",
    "loginout_panel",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "DIRS": [],
    },
]

# Only our panel, so DebugToolbar.get_panel_by_id("LoginOutPanel") is unambiguous.
DEBUG_TOOLBAR_PANELS = [
    "loginout_panel.panel.LoginOutPanel",
]

# The account the panel logs in as, under test.
LOGINOUT_USERNAME = "tester"

USE_TZ = True
