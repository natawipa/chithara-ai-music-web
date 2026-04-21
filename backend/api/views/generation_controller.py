"""
Handles AI song generation process.

- Create generation request
- Validate input
- Track status
- Cancel generation
"""

import json
import logging

from django.core.exceptions import ValidationError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from api.decorators import json_login_required
from api.models import GenerationRequest
from api.models.enums import GenerationStatus
from api.services.generation import get_song_generator
from api.services.generation_service import SongGenerationService
from api.services.suno_service import InsufficientCreditError

logger = logging.getLogger(__name__)


def _song_data(song) -> dict:
    """Serialise a Song instance to a plain dict for JSON responses."""
    return {
        "id": song.id,
        "title": song.title,
        "audio_file": song.audio_file,
        "cover_image": song.cover_image.url if song.cover_image else None,
        "cover_color": song.cover_color,
        "genre": song.genre,
        "tone": song.tone,
        "occasion": song.occasion,
        "privacy_level": song.privacy_level,
        "created_at": song.created_at.isoformat(),
    }


# Views
@json_login_required
@require_POST
def create(request):
    """Create a GenerationRequest and immediately submit it to Suno.

    POST /api/generate/
    Body (JSON): title (required), description (required), genre (required),
                 tone (optional), occasion (optional)

    Returns:
        202 { id, status: "PROCESSING" } on success.
        400 on missing/invalid fields or Suno submission failure.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    title = body.get("title", "").strip()
    description = body.get("description", "").strip()
    genre = body.get("genre", "").strip()
    tone = body.get("tone", "").strip()
    occasion = body.get("occasion", "").strip()

    if not all([title, description, genre]):
        return JsonResponse(
            {"error": "title, description, and genre are required."},
            status=400,
        )

    generation_request = GenerationRequest.objects.create(
        user=request.user,
        title=title,
        description=description,
        genre=genre,
        tone=tone,
        occasion=occasion,
        generator_strategy=settings.GENERATOR_STRATEGY,
    )

    try:
        get_song_generator(generation_request.generator_strategy)
        SongGenerationService().submit_generation(generation_request)

    except InsufficientCreditError:
        generation_request.mark_failed("Out of credit")
        return JsonResponse({"error": "Out of credit"}, status=400)

    except Exception as exc:
        if generation_request.status != GenerationStatus.FAILED:
            logger.exception(
                "Generation submission failed for GenerationRequest %s",
                generation_request.id,
            )
            generation_request.mark_failed(str(exc))
        return JsonResponse(
            {"error": "Failed to submit generation request.", "detail": str(exc)},
            status=502,
        )

    generation_request.refresh_from_db(fields=["status"])

    return JsonResponse(
        {
            "id": generation_request.id,
            "status": generation_request.status,
            "generator_strategy": generation_request.generator_strategy,
            "external_task_id": generation_request.external_task_id,
        },
        status=202,
    )


@json_login_required
def status(request, id):
    """Return the current status of a generation request.

    GET /api/generate/<id>/status/

    Status is updated asynchronously via the Suno callback endpoint.
    This view returns the latest persisted state.

    Returns:
        200 { id, status, song } — song is null unless COMPLETED.
        403 when the request belongs to another user.
        404 when the request does not exist.
    """
    try:
        generation_request = GenerationRequest.objects.select_related(
            "song"
        ).get(id=id, user=request.user)
    except GenerationRequest.DoesNotExist:
        # Use 404 for both missing and wrong-owner to avoid ID enumeration.
        return JsonResponse({"error": "Generation request not found."}, status=404)

    if (
        generation_request.status == GenerationStatus.PROCESSING
    ):
        try:
            SongGenerationService().sync_generation_status(generation_request)
            generation_request.refresh_from_db(fields=["status", "song", "error_message"])
        except Exception:
            logger.exception("Failed to sync GenerationRequest %s", generation_request.id)

    song = None
    if generation_request.status == GenerationStatus.COMPLETED and generation_request.song:
        song = _song_data(generation_request.song)

    return JsonResponse(
        {
            "id": generation_request.id,
            "status": generation_request.status,
            "generator_strategy": generation_request.generator_strategy,
            "external_task_id": generation_request.external_task_id,
            "song": song,
            "error": generation_request.error_message or None,
        }
    )


@json_login_required
@require_POST
def cancel(request, id):
    """Cancel a pending generation request.

    POST /api/generate/<id>/cancel/

    Cancellation prevents a queued request from being submitted to Suno.
    Requests that are already COMPLETED cannot be cancelled.

    Returns:
        200 { id, status: "CANCELLED" }.
        400 if the request cannot be cancelled (e.g. already completed).
        404 when the request does not exist or belongs to another user.
    """
    try:
        generation_request = GenerationRequest.objects.get(
            id=id, user=request.user
        )
    except GenerationRequest.DoesNotExist:
        return JsonResponse({"error": "Generation request not found."}, status=404)

    try:
        generation_request.cancel()
    except ValidationError as exc:
        return JsonResponse({"error": str(exc.message)}, status=400)

    return JsonResponse(
        {"id": generation_request.id, "status": generation_request.status}
    )
