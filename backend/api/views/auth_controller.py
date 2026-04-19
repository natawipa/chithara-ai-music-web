"""Authentication views for Google OAuth + session-based auth."""

import logging
import secrets
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_GET, require_POST

from api.decorators import json_login_required

logger = logging.getLogger(__name__)
User = get_user_model()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


@require_GET
def login(request):
    """Start Google OAuth by redirecting to the consent page."""
    state = secrets.token_urlsafe(24)
    request.session["google_oauth_state"] = state

    query = urlencode(
        {
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "access_type": "online",
            "prompt": "select_account",
        }
    )
    return HttpResponseRedirect(f"{GOOGLE_AUTH_URL}?{query}")


@require_GET
def google_callback(request):
    """Handle Google OAuth callback and create/login local user."""
    code = request.GET.get("code")
    state = request.GET.get("state")
    expected_state = request.session.pop("google_oauth_state", None)

    if not code:
        return JsonResponse({"error": "Missing authorization code."}, status=400)

    if not state or state != expected_state:
        return JsonResponse({"error": "Invalid OAuth state."}, status=400)

    try:
        token_response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        token_response.raise_for_status()
        access_token = token_response.json().get("access_token")

        if not access_token:
            return JsonResponse({"error": "Missing access token."}, status=400)

        profile_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=15,
        )
        profile_response.raise_for_status()
        profile = profile_response.json()
    except requests.RequestException as exc:
        logger.exception("Google OAuth request failed: %s", exc)
        return JsonResponse({"error": "Failed to authenticate with Google."}, status=502)

    google_id = profile.get("id")
    email = profile.get("email", "")
    given_name = profile.get("given_name", "")
    family_name = profile.get("family_name", "")

    if not google_id:
        return JsonResponse({"error": "Google profile is missing id."}, status=400)

    username_base = (email.split("@")[0] if email else f"google_{google_id}")[:120]
    username = username_base
    suffix = 1
    while User.objects.filter(username=username).exclude(google_id=google_id).exists():
        username = f"{username_base}_{suffix}"[:150]
        suffix += 1

    user, created = User.objects.get_or_create(
        google_id=google_id,
        defaults={
            "username": username,
            "email": email,
            "first_name": given_name,
            "last_name": family_name,
        },
    )

    if not created:
        changed = False
        if email and user.email != email:
            user.email = email
            changed = True
        if given_name and user.first_name != given_name:
            user.first_name = given_name
            changed = True
        if family_name and user.last_name != family_name:
            user.last_name = family_name
            changed = True
        if changed:
            user.save(update_fields=["email", "first_name", "last_name"])

    auth_login(request, user)

    frontend_redirect = getattr(settings, "FRONTEND_APP_URL", "http://localhost:5173/library")
    return HttpResponseRedirect(frontend_redirect)


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
