#!/usr/bin/env python
"""Run the django-loginout-panel demo project."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_site.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you in the demo's virtualenv with "
            "django-loginout-panel installed? Try `pip install -e ..` and "
            "`pip install django-debug-toolbar`."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
