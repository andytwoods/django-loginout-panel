from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.http import JsonResponse


def _get_client_ip(request):
    # from https://stackoverflow.com/a/5976065/960471
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR")


def on_local_server(view):
    """Restrict a view to requests from LOGINOUT_SERVER, when that is set.

    If LOGINOUT_SERVER is not configured, the view is allowed through: the
    panel is only ever mounted behind the debug toolbar, which is itself
    gated by SHOW_TOOLBAR_CALLBACK / DEBUG.
    """

    def wrapper(request, *args, **kwargs):
        allowed = getattr(settings, "LOGINOUT_SERVER", None)
        if allowed is not None and allowed != _get_client_ip(request):
            return JsonResponse({}, status=404)
        return view(request, *args, **kwargs)

    return wrapper


def _resolve_user():
    User = get_user_model()
    username = getattr(settings, "LOGINOUT_USERNAME", None)
    if not username:
        return None
    return User.objects.filter(**{User.USERNAME_FIELD: username}).first()


@on_local_server
def login_view(request):
    user = _resolve_user()
    if user is None:
        return JsonResponse(
            {"error": "LOGINOUT_USERNAME is not set or no matching user exists."},
            status=400,
        )
    backend = settings.AUTHENTICATION_BACKENDS[0]
    login(request, user, backend=backend)
    return JsonResponse({"status": "logged-in", "user": str(user)})


@on_local_server
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "logged-out"})
