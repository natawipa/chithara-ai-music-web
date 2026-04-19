from django.db import transaction

from api.models import Song
from api.services.cover_service import attach_cover_from_url, generate_random_color

import logging

from .suno_service import SunoService

logger = logging.getLogger(__name__)


class SunoServiceProxy:
    """Wrap SunoService and persist generation state inside the application."""

    def __init__(self, service=None):
        self._service = service or SunoService()

    def generate_song(self, generation_request, data: dict) -> str:
        """Submit a generation request and persist the returned external task ID."""
        task_id = self._service.generate_song(data)
        generation_request.external_task_id = task_id
        generation_request.save(update_fields=["external_task_id", "updated_at"])
        return task_id

    def sync_generation_status(self, generation_request):
        """Poll Suno for the latest status and persist state transitions locally."""
        task_id = generation_request.external_task_id
        if not task_id or generation_request.song_id:
            return generation_request.song

        result = self._service.get_status(task_id)
        status = result.get("status")
        if status == "completed":
            audio_url = result.get("audio_url")
            if audio_url:
                return self.store_generated_song(
                    generation_request,
                    audio_url,
                    cover_image_url=result.get("image_url"),
                )
        elif status == "failed":
            generation_request.mark_failed(result.get("error") or "Unknown error from Suno.")

        return generation_request.song

    def store_generated_song(
        self,
        generation_request,
        audio_url: str,
        cover_image_url: str | None = None,
    ) -> Song:
        """Create and attach the generated Song for a completed request."""
        with transaction.atomic():
            generation_request.refresh_from_db(fields=["song"])
            if generation_request.song_id:
                return generation_request.song

            song = Song.objects.create(
                title=generation_request.title,
                description=generation_request.description,
                genre=generation_request.genre,
                tone=generation_request.tone,
                occasion=generation_request.occasion,
                audio_file=audio_url,
                cover_color="",
                user=generation_request.user,
            )

            update_fields = ["updated_at"]
            if cover_image_url:
                try:
                    if attach_cover_from_url(song, cover_image_url):
                        update_fields.extend(["cover_image", "cover_color"])
                except Exception:
                    logger.exception(
                        "Failed to download Suno cover image for GenerationRequest %s",
                        generation_request.id,
                    )

            if not song.cover_image:
                song.cover_color = generate_random_color()
                update_fields.append("cover_color")

            song.save(update_fields=update_fields)
            generation_request.mark_completed(song)
            return song
