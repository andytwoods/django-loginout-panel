# django-loginout-panel demo

A tiny throwaway Django project that shows the panel in action: the home page
displays a **Logged in / Logged out** banner, and the debug toolbar's
**Login / out** panel flips between the two with one click.

## Zero-install (recommended)

If you have [uv](https://docs.astral.sh/uv/), you can run the single-file
version straight from GitHub – no clone, no virtualenv, no `pip install`:

```bash
uv run https://raw.githubusercontent.com/andytwoods/django-loginout-panel/master/demo/app.py
```

uv reads the inline dependency block at the top of [`app.py`](app.py), provisions
a matching Python and all dependencies in a throwaway environment, seeds a `demo`
user, and starts the dev server. Open <http://127.0.0.1:8000/> and use the panel.

To run the same single file from a local checkout:

```bash
uv run demo/app.py
```

## From a checkout (multi-file project)

A conventional, readable project layout lives alongside the single file. From a
clone:

```bash
cd demo
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ..          # install django-loginout-panel from this repo
pip install django-debug-toolbar

python manage.py migrate
python manage.py seed      # creates the "demo" user the panel logs in as
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

## Recording the README GIF

1. Start the demo (either method above) and open the home page.
2. Open the debug toolbar and select the **Login / out** panel.
3. Record: click **log in** (banner turns green, "Logged in as demo"), then
   **log out** (banner returns to grey). The page reloads on each click.
4. Save the recording as `images/demo.gif` (at the repo root) so the main
   README displays it at the top of the page.
