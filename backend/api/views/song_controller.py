"""
Handles operations on existing songs.

- Edit song metadata
- Delete song
- Update privacy level
- Ensure ownership validation
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from api.decorators import json_login_required
from api.models import Song
from api.models.enums import PrivacyLevel

logger = logging.getLogger(__name__)


@json_login_required
@require_POST
def update(request, id):
    """Update a song's title and/or description.

    POST /api/songs/<id>/update/
    Body (JSON): title (optional), description (optional)

    Ownership is enforced: a user cannot update another user's song.

    Returns:
        200 { id, title, description } on success.
        400 on invalid JSON or no updatable fields provided.
        401 when unauthenticated.
        404 when the song does not exist or belongs to another user.
    """
    try:
        song = Song.objects.get(id=id, user=request.user)
    except Song.DoesNotExist:
        # Return 404 for both missing and wrong-owner to avoid ID enumeration.
        return JsonResponse({"error": "Song not found."}, status=404)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    title = body.get("title", "").strip()
    description = body.get("description")  # None = "not provided"

    if not title and description is None:
        return JsonResponse(
            {"error": "Provide at least one field to update: title, description."},
            status=400,
        )

    update_fields = ["updated_at"]

    if title:
        song.title = title
        update_fields.append("title")

    if description is not None:
        song.description = description.strip()
        update_fields.append("description")

    song.save(update_fields=update_fields)

    return JsonResponse(
        {"id": song.id, "title": song.title, "description": song.description}
    )


@json_login_required
def delete(request, id):
    """Permanently delete a song owned by the authenticated user.

    DELETE /api/songs/<id>/delete/

    Returns:
        200 { message } on success.
        401 when unauthenticated.
        404 when the song does not exist or belongs to another user.
    """
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed."}, status=405)

    try:
        song = Song.objects.get(id=id, user=request.user)
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)

    song.delete()
    return JsonResponse({"message": "Song deleted."})


@json_login_required
@require_POST
def set_privacy(request, id):
    """Update the privacy level of a song.

    POST /api/songs/<id>/privacy/
    Body (JSON): privacy_level ("PRIVATE" | "PUBLIC")

    Returns:
        200 { id, privacy_level } on success.
        400 on invalid or missing privacy_level value.
        401 when unauthenticated.
        404 when the song does not exist or belongs to another user.
    """
    try:
        song = Song.objects.get(id=id, user=request.user)
    except Song.DoesNotExist:
        return JsonResponse({"error": "Song not found."}, status=404)

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    privacy_level = body.get("privacy_level", "").strip().upper()
    valid_levels = [choice.value for choice in PrivacyLevel]

    if privacy_level not in valid_levels:
        return JsonResponse(
            {"error": f"Invalid privacy_level. Choose from: {valid_levels}."},
            status=400,
        )

    song.privacy_level = privacy_level
    song.save(update_fields=["privacy_level", "updated_at"])

    return JsonResponse({"id": song.id, "privacy_level": song.privacy_level})
