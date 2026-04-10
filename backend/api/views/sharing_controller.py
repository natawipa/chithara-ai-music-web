"""
Handles song sharing features.

- Generate share link (authenticated)
- Access shared songs via token (public)
- Validate permissions
"""

import logging

from django.core import signing
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from api.decorators import json_login_required
from api.models import Song

logger = logging.getLogger(__name__)

# Cryptographic salt scoped to sharing — prevents token reuse across features.
_SHARE_SALT = "song-share-v1"

# Tokens expire after 7 days (in seconds).
_SHARE_TOKEN_MAX_AGE = 7 * 24 * 60 * 60


def _build_share_url(request, token: str) -> str:
    """Construct the full share URL for the given token."""
    return f"{request.scheme}://{request.get_host()}/api/songs/share/{token}/"


# Views
@json_login_required
@require_POST
def share(request, id):
    """Generate a signed share token for a song the user owns.

    POST /api/songs/<id>/share/

    The token is signed with Django's cryptographic signing module —
    no extra database column is required. Tokens expire after 7 days.

    Ownership is enforced: users cannot generate share links for other
    users' songs.

    Returns:
        200 { token, share_url, expires_in_days: 7 }
        401 when unauthenticated.
        404 when the song does not exist or belongs to another user.
    """
    try:
        song = Song.objects.get(id=id, user=request.user)
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)

    # signing.dumps embeds a timestamp; signing.loads will verify it on access.
    token = signing.dumps(song.id, salt=_SHARE_SALT)
    share_url = _build_share_url(request, token)

    return JsonResponse(
        {
            "token": token,
            "share_url": share_url,
            "expires_in_days": 7,
        }
    )


@require_GET
def access(request, token):
    """Return a song's public data using a valid share token.

    GET /api/songs/share/<token>/

    This endpoint is intentionally PUBLIC — no authentication is required.
    Authorization is granted by possession of a valid, unexpired token.

    Returns:
        200 { id, title, genre, tone, occasion, audio_file, created_at }
        400 when the token is malformed or tampered with.
        404 when the referenced song no longer exists.
        410 when the share token has expired.
    """
    try:
        song_id = signing.loads(
            token,
            salt=_SHARE_SALT,
            max_age=_SHARE_TOKEN_MAX_AGE,
        )
    except signing.SignatureExpired:
        return JsonResponse({"error": "Share link has expired."}, status=410)
    except signing.BadSignature:
        return JsonResponse({"error": "Invalid share token."}, status=400)

    try:
        song = Song.objects.get(id=song_id)
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)

    return JsonResponse(
        {
            "id": song.id,
            "title": song.title,
            "genre": song.genre,
            "tone": song.tone,
            "occasion": song.occasion,
            "audio_file": song.audio_file,
            "created_at": song.created_at.isoformat(),
        }
    )
