#!/usr/bin/env python
"""Run the test suite with Django's own runner – no pytest required.

CI runs the suite through pytest/tox (matching the mrbenn conventions), but
this gives a zero-extra-dependency way to run everything locally:

    python testrunner.py
"""
import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")


def main():
    django.setup()
    from django.test.runner import DiscoverRunner

    failures = DiscoverRunner(verbosity=2).run_tests(["tests"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
