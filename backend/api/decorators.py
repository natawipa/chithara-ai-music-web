import functools

from django.http import JsonResponse


def json_login_required(view_func):
    """Enforce authentication and return JSON 401 instead of redirecting.

    Drop-in replacement for Django's @login_required suited for API views
    that speak JSON rather than HTML.

    Usage::

        @json_login_required
        def my_view(request):
            ...
    """
    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required."}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper
