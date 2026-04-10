"""
Handles authentication using Google OAuth.

- Login (OAuth flow)
- Callback handling
- Logout
- Get current user
"""

import logging

from django.contrib.auth import logout as auth_logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from api.decorators import json_login_required

logger = logging.getLogger(__name__)


def login(request):
    """Placeholder for Google OAuth login initiation.

    GET /api/auth/login/

    In production this redirects the user to Google's OAuth consent screen.
    The token exchange is handled via the OAuth callback URL configured in
    GOOGLE_OAUTH_REDIRECT_URI.

    Returns:
        200 { message } — placeholder until OAuth is fully integrated.
    """
    # TODO: build and redirect to Google OAuth consent screen using
    # settings.GOOGLE_OAUTH_CLIENT_ID and settings.GOOGLE_OAUTH_REDIRECT_URI
    return JsonResponse({"message": "Google OAuth login not yet implemented."})


@json_login_required
def me(request):
    """Return the profile of the currently authenticated user.

    GET /api/auth/me/

    Returns:
        200 { id, username, email, first_name, last_name }
        401 when not authenticated.
    """
    user = request.user
    return JsonResponse(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    )


@json_login_required
@require_POST
def logout(request):
    """Log out the current session.

    POST /api/auth/logout/

    Invalidates the server-side session. The client should discard any
    stored session cookies or tokens.

    Returns:
        200 { message } on success.
        401 when not authenticated.
    """
    auth_logout(request)
    return JsonResponse({"message": "Logged out successfully."})
