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

from api.models import GenerationRequest
from api.services.suno_service_proxy import SunoServiceProxy

logger = logging.getLogger(__name__)

proxy = SunoServiceProxy()


def _parse_callback_payload(
    body: dict,
) -> tuple[str | None, str, str | None, str | None, str | None]:
    """Normalise Suno callback payloads into task ID, status, audio URL, image URL, and error."""
    data = body.get("data") if isinstance(body.get("data"), dict) else {}
    callback_type = str(data.get("callbackType") or body.get("status") or "").lower()

    items = data.get("data") if isinstance(data.get("data"), list) else []
    first_item = items[0] if items and isinstance(items[0], dict) else {}

    task_id = (
        data.get("task_id")
        or data.get("taskId")
        or body.get("task_id")
        or body.get("taskId")
    )
    audio_url = (
        first_item.get("audio_url")
        or first_item.get("audioUrl")
        or body.get("audioUrl")
        or body.get("audio_url")
    )
    image_url = (
        first_item.get("image_url")
        or first_item.get("imageUrl")
        or first_item.get("source_image_url")
        or first_item.get("sourceImageUrl")
        or body.get("imageUrl")
        or body.get("image_url")
    )
    error = body.get("msg") or data.get("error") or body.get("error")

    if callback_type == "complete":
        status = "completed"
    elif callback_type == "error":
        status = "failed"
    else:
        status = callback_type

    return task_id, status, audio_url, image_url, error


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

    task_id, status, audio_url, image_url, error = _parse_callback_payload(body)

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

        song = proxy.store_generated_song(generation_request, audio_url, image_url)
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
