# django-loginout-panel

A [Django Debug Toolbar](https://github.com/jazzband/django-debug-toolbar) panel
that logs a configured user **in or out with one click** – handy during local
development when you constantly need to jump between an authenticated and an
anonymous session.

The panel adds a small **log in / log out** control to the toolbar sidebar. Each
click hits a tiny JSON endpoint that calls Django's `login()` / `logout()` for a
username you configure, then reloads the page.

## Requirements

- Python 3.8+
- Django 3.2+
- django-debug-toolbar 3.2+

## Installation

```bash
pip install django-loginout-panel
```

Or straight from a git checkout:

```bash
pip install git+https://github.com/andytwoods/django-loginout-panel.git
```

## Setup

This is a **development-only** tool. Add it alongside your existing debug
toolbar configuration – typically in a `local.py` / `dev.py` settings module,
never in production.

```python
# settings/local.py

INSTALLED_APPS += [
    "debug_toolbar",
    "loginout_panel",
]

DEBUG_TOOLBAR_PANELS = [
    "loginout_panel.LoginOutPanel",
    # ... your other panels ...
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.sql.SQLPanel",
]

# The user to log in as when you click "log in".
LOGINOUT_USERNAME = "me@example.com"

# Optional: only allow the panel's endpoints from this client IP.
# Leave unset to rely on the toolbar's own SHOW_TOOLBAR_CALLBACK / DEBUG gate.
LOGINOUT_SERVER = "127.0.0.1"
```

Make sure `debug_toolbar` is otherwise wired up as usual (middleware +
`urls.py`), per the
[debug toolbar install docs](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html).

### Settings reference

| Setting | Required | Purpose |
| --- | --- | --- |
| `LOGINOUT_USERNAME` | yes | Username (matched against your user model's `USERNAME_FIELD`) to log in as. |
| `LOGINOUT_SERVER` | no | If set, only requests from this client IP may use the login/logout endpoints; all others get a `404`. |

The login view authenticates using `settings.AUTHENTICATION_BACKENDS[0]`, so make
sure your first backend is the one you want (Django's default
`ModelBackend` works fine).

## Usage

1. Run your dev server and open any page with the debug toolbar visible.
2. Find the **Login / out** panel in the toolbar.
3. Click **log in** to become `LOGINOUT_USERNAME`, or **log out** to drop to an
   anonymous session. The page reloads automatically.

Clicking the panel itself opens a body showing the current auth status and the
configured username.

## How it works

- `LoginOutPanel` subclasses `debug_toolbar.panels.Panel` and registers two
  URLs under the toolbar's `djdt` namespace: `loginout_login` and
  `loginout_logout`.
- The endpoints return JSON and are wrapped in an `on_local_server` decorator
  that enforces `LOGINOUT_SERVER` when configured.
- No models, no migrations – it only reads settings and calls the standard auth
  functions.

## Security note

Never enable this in production. It provides an unauthenticated way to log in as
an arbitrary account. Keep it in a dev-only settings module, behind the debug
toolbar (which itself should only run with `DEBUG = True` and a restrictive
`SHOW_TOOLBAR_CALLBACK`). `LOGINOUT_SERVER` is an extra belt-and-braces IP check.

## License

MIT – see [LICENSE](LICENSE).
