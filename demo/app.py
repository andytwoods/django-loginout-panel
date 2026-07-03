# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "django>=5.2",
#     "django-debug-toolbar>=6.0",
#     "django-loginout-panel",
# ]
# ///
"""Single-file, zero-install demo of django-loginout-panel.

Run it straight from the web with uv – no clone, no manual virtualenv:

    uv run https://raw.githubusercontent.com/andytwoods/django-loginout-panel/master/demo/app.py

uv reads the inline dependency block above, provisions a matching Python and
all dependencies in a throwaway environment, then starts the dev server. Open
http://127.0.0.1:8000/ and use the "Login / out" panel in the debug toolbar.
"""

import os
import sys
import tempfile

from django.conf import settings

# A file-based SQLite db in the temp dir keeps the working directory clean while
# still surviving across the dev server's request threads.
DB_PATH = os.path.join(tempfile.gettempdir(), "loginout_panel_demo.sqlite3")

if not settings.configured:
    settings.configure(
        # The panel is deliberately dev-only; it 404s unless DEBUG is on.
        DEBUG=True,
        SECRET_KEY="demo-only-not-a-secret",
        ALLOWED_HOSTS=["127.0.0.1", "localhost"],
        INTERNAL_IPS=["127.0.0.1"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.staticfiles",
            "debug_toolbar",
            "loginout_panel",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "debug_toolbar.middleware.DebugToolbarMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": DB_PATH,
            }
        },
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
                "DIRS": [],
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                    ],
                },
            }
        ],
        STATIC_URL="static/",
        USE_TZ=True,
        DEBUG_TOOLBAR_PANELS=[
            "loginout_panel.LoginOutPanel",
            "debug_toolbar.panels.request.RequestPanel",
            "debug_toolbar.panels.sql.SQLPanel",
        ],
        LOGINOUT_USERNAME="demo",
    )

import django  # noqa: E402

django.setup()

from debug_toolbar.toolbar import debug_toolbar_urls  # noqa: E402
from django.http import HttpResponse  # noqa: E402
from django.urls import path  # noqa: E402

# The debug toolbar injects itself before </body>, so a plain HTML response is
# enough – no template files needed for the single-file demo.
HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>django-loginout-panel demo</title>
<style>
  body { margin: 0; min-height: 100vh; display: flex; align-items: center;
    justify-content: center; background: #0f172a; color: #e2e8f0;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; }
  .card { text-align: center; padding: 3rem 3.5rem; border-radius: 18px;
    background: #1e293b; box-shadow: 0 20px 60px rgba(0,0,0,.45); }
  .status { font-size: 2.4rem; font-weight: 700; margin: 0 0 .4rem; }
  .in .status { color: #4ade80; }
  .out .status { color: #94a3b8; }
  .who { font-size: 1.1rem; color: #cbd5e1; margin: 0; }
  .hint { margin-top: 1.6rem; font-size: .95rem; color: #64748b; }
  .dot { display: inline-block; width: .7rem; height: .7rem; border-radius: 50%;
    margin-right: .5rem; vertical-align: middle; }
  .in .dot { background: #4ade80; box-shadow: 0 0 12px #4ade80; }
  .out .dot { background: #64748b; }
</style></head><body>
"""
FOOT = "\n</body></html>"


def index(request):
    if request.user.is_authenticated:
        card = (
            '<div class="card in"><p class="status"><span class="dot"></span>'
            "Logged in</p><p class=\"who\">You are authenticated as <strong>"
            f"{request.user.get_username()}</strong>.</p>"
        )
    else:
        card = (
            '<div class="card out"><p class="status"><span class="dot"></span>'
            'Logged out</p><p class="who">You are browsing anonymously.</p>'
        )
    hint = (
        '<p class="hint">Use the <strong>Login / out</strong> panel in the '
        "debug toolbar &rarr;</p></div>"
    )
    return HttpResponse(HEAD + card + hint + FOOT)


urlpatterns = [path("", index, name="home")] + debug_toolbar_urls()


def main():
    from django.contrib.auth import get_user_model
    from django.core.management import call_command, execute_from_command_line

    call_command("migrate", run_syncdb=True, verbosity=0)

    User = get_user_model()
    username = settings.LOGINOUT_USERNAME
    if not User.objects.filter(**{User.USERNAME_FIELD: username}).exists():
        User.objects.create_user(username, password="demo")
        print(f"Created demo user {username!r}.")

    argv = sys.argv
    if len(argv) == 1:
        print("\nDemo running at http://127.0.0.1:8000/  (press Ctrl-C to stop)\n")
        argv = [argv[0], "runserver", "--noreload", "127.0.0.1:8000"]
    execute_from_command_line(argv)


if __name__ == "__main__":
    main()
