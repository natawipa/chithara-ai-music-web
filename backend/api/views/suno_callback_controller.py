"""
Handles Suno webhook callbacks.

Suno POSTs to this endpoint when a generation task completes or fails.
No user authentication is required — the request originates from Suno's servers.
CSRF protection is disabled because Suno cannot send a CSRF token.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from api.models import GenerationRequest, Song

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def suno_callback(request):
    """Receive a generation result from Suno and update the database.

    POST /api/suno/callback/
    Payload (JSON): taskId, status, audioUrl, error

    Status values from Suno:
        "completed" → create Song and mark the request as COMPLETED.
        "failed"    → mark the request as FAILED with the error message.
        other       → logged and ignored (e.g. intermediate progress events).

    Returns:
        200 { message: "callback processed" } in all handled cases.
        400 on missing required fields or invalid JSON.
        404 if no GenerationRequest matches the taskId.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    task_id = body.get("taskId")
    status = body.get("status", "").lower()
    audio_url = body.get("audioUrl")
    error = body.get("error")

    if not task_id:
        return JsonResponse({"error": "taskId is required."}, status=400)

    # Locate the matching generation request
    try:
        generation_request = GenerationRequest.objects.select_related("user").get(
            external_task_id=task_id
        )
    except GenerationRequest.DoesNotExist:
        logger.warning("Callback received for unknown taskId: %s", task_id)
        return JsonResponse({"error": "Generation request not found."}, status=404)

    if status == "completed":
        if not audio_url:
            return JsonResponse(
                {"error": "audioUrl is required for completed status."},
                status=400,
            )

        # Build the Song from the original request's stored fields
        song = Song.objects.create(
            title=generation_request.title,
            description=generation_request.description,
            genre=generation_request.genre,
            tone=generation_request.tone,
            occasion=generation_request.occasion,
            audio_file=audio_url,
            user=generation_request.user,
        )

        generation_request.mark_completed(song)
        logger.info(
            "GenerationRequest %s completed — Song %s created.",
            generation_request.id,
            song.id,
        )

    elif status == "failed":
        error_message = error or "Unknown error from Suno."
        generation_request.mark_failed(error_message)
        logger.warning(
            "GenerationRequest %s failed: %s", generation_request.id, error_message
        )

    else:
        # Intermediate or unrecognised status — log and acknowledge
        logger.info(
            "Ignoring callback with unhandled status '%s' for taskId %s",
            status,
            task_id,
        )

    return JsonResponse({"message": "callback processed"})
