__all__ = ["LoginOutPanel"]
__version__ = "0.1.0"


def __getattr__(name):
    # Import the panel (and, transitively, the views that decorate themselves
    # with debug-toolbar helpers) lazily. Because this package is listed in
    # INSTALLED_APPS, an eager import here would run during app population –
    # before django-debug-toolbar's own app is ready – and importing its
    # decorators pulls in debug_toolbar.models, raising AppRegistryNotReady.
    # Resolving on attribute access defers it until the toolbar is built.
    if name == "LoginOutPanel":
        from .panel import LoginOutPanel

        return LoginOutPanel
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
