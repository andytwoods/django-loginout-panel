# django-loginout-panel

![Logging in and out from the debug toolbar panel](https://raw.githubusercontent.com/andytwoods/django-loginout-panel/master/images/demo.gif)

A [Django Debug Toolbar](https://github.com/jazzband/django-debug-toolbar) panel
that logs a configured user **in or out with one click** – handy during local
development when you constantly need to jump between an authenticated and an
anonymous session.

The panel adds a small **log in / log out** control to the toolbar sidebar. Each
click hits a tiny JSON endpoint that calls Django's `login()` / `logout()` for a
username you configure, then reloads the page.

## Try it (no install)

With [uv](https://docs.astral.sh/uv/) you can run a self-contained demo straight
from GitHub – no clone, no virtualenv, no `pip install`:

```bash
uv run https://raw.githubusercontent.com/andytwoods/django-loginout-panel/master/demo/app.py
```

uv provisions a matching Python and all dependencies in a throwaway environment,
then serves the demo at <http://127.0.0.1:8000/>. See [`demo/`](demo/) for a
conventional multi-file version and more detail.

## Requirements

- Python 3.12+
- Django 5.2+
- django-debug-toolbar 6.0+

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
    "loginout_panel.panel.LoginOutPanel",
    # ... your other panels ...
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.sql.SQLPanel",
]

# The user to log in as when you click "log in".
LOGINOUT_USERNAME = "me@example.com"

# Optional: only allow the panel's endpoints from this client IP.
# Leave unset to rely on the toolbar's own SHOW_TOOLBAR_CALLBACK / DEBUG gate.
LOGINOUT_SERVER = "127.0.0.1"

# Optional: trust the X-Forwarded-For header when matching LOGINOUT_SERVER.
# Only enable this behind a reverse proxy that overwrites the header; otherwise
# a client can spoof the allowed IP. Defaults to False (REMOTE_ADDR is used).
LOGINOUT_TRUST_XFF = False
```

Make sure `debug_toolbar` is otherwise wired up as usual (middleware +
`urls.py`), per the
[debug toolbar install docs](https://django-debug-toolbar.readthedocs.io/en/latest/installation.html).

### Settings reference

| Setting | Required | Purpose |
| --- | --- | --- |
| `LOGINOUT_USERNAME` | yes | Username (matched against your user model's `USERNAME_FIELD`) to log in as. Only **active** users are eligible. |
| `LOGINOUT_SERVER` | no | If set, only requests from this client IP may use the login/logout endpoints; all others get a `404`. |
| `LOGINOUT_TRUST_XFF` | no | Trust `X-Forwarded-For` when resolving the client IP for `LOGINOUT_SERVER`. Enable only behind a trusted reverse proxy. Defaults to `False`. |

The login view authenticates using `settings.AUTHENTICATION_BACKENDS[0]` (falling
back to Django's `ModelBackend` when the setting is unset), so make sure your
first backend is the one you want.

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
- The endpoints return JSON and are **POST-only, CSRF-protected**, and layered
  behind the toolbar's own `SHOW_TOOLBAR_CALLBACK`, an explicit `settings.DEBUG`
  check, and the optional `on_local_server` (`LOGINOUT_SERVER`) IP guard. Any of
  those failing yields a `404` (or `405`/`403` for wrong method / missing token).
- No models, no migrations – it only reads settings and calls the standard auth
  functions.

## Security note

Never enable this in production. It provides an unauthenticated way to log in as
an arbitrary account. It is defended in depth so an accidental production deploy
still fails closed:

- **POST + CSRF only.** The endpoints reject `GET` and require a CSRF token, so a
  stray `<img src>`/link cannot silently log a browser in.
- **`DEBUG` gate.** They `404` whenever `settings.DEBUG` is off – independent of
  the toolbar's callback, which a project might loosen to show the toolbar to
  staff in production.
- **Toolbar callback.** They also honour `SHOW_TOOLBAR_CALLBACK`, so they are
  only reachable where the toolbar itself is.
- **Active users only, first backend.** Only active accounts can be logged in,
  via `AUTHENTICATION_BACKENDS[0]`.
- **`LOGINOUT_SERVER`** is an extra belt-and-braces IP check. `X-Forwarded-For`
  is ignored unless you explicitly opt in with `LOGINOUT_TRUST_XFF` behind a
  trusted proxy, so the allowlist cannot be spoofed by default.

Still: keep it in a dev-only settings module and never ship it enabled.

## License

MIT – see [LICENSE](LICENSE).
