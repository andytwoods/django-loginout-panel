import functools

from debug_toolbar.decorators import require_show_toolbar
from django.conf import settings
from django.contrib.auth import get_user_model, login, logout
from django.http import Http404, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST


def _get_client_ip(request):
    """Return the client IP used for the LOGINOUT_SERVER allowlist.

    ``X-Forwarded-For`` is only consulted when LOGINOUT_TRUST_XFF is truthy,
    because a client can set that header freely unless a trusted reverse proxy
    overwrites it – trusting it by default would let anyone spoof the allowed
    IP. When trusted, the last hop (the address the closest proxy saw) is used.
    """
    if getattr(settings, "LOGINOUT_TRUST_XFF", False):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR")


def _debug_only(view):
    """404 the view unless ``settings.DEBUG`` is on.

    Independent of the toolbar's SHOW_TOOLBAR_CALLBACK: a project may override
    that callback to reveal the toolbar to (say) staff users in production, and
    a passwordless login endpoint must never be reachable there.
    """

    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        if not settings.DEBUG:
            raise Http404
        return view(request, *args, **kwargs)

    return wrapper


def on_local_server(view):
    """Restrict a view to requests from LOGINOUT_SERVER, when that is set.

    If LOGINOUT_SERVER is not configured, the view is allowed through: it is
    already gated by the debug toolbar's SHOW_TOOLBAR_CALLBACK and a DEBUG
    check (see the decorator stack below).
    """

    @functools.wraps(view)
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
    return User.objects.filter(
        **{User.USERNAME_FIELD: username, "is_active": True}
    ).first()


@require_show_toolbar
@_debug_only
@require_POST
@csrf_protect
@on_local_server
def login_view(request):
    user = _resolve_user()
    if user is None:
        return JsonResponse(
            {"error": "LOGINOUT_USERNAME is not set or no matching active user exists."},
            status=400,
        )
    backends = getattr(settings, "AUTHENTICATION_BACKENDS", None) or [
        "django.contrib.auth.backends.ModelBackend"
    ]
    login(request, user, backend=backends[0])
    return JsonResponse({"status": "logged-in", "user": str(user)})


@require_show_toolbar
@_debug_only
@require_POST
@csrf_protect
@on_local_server
def logout_view(request):
    logout(request)
    return JsonResponse({"status": "logged-out"})
