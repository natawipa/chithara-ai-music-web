from __future__ import annotations

import logging

from django.db import transaction

from api.models import Song
from api.models.enums import Genre
from api.services.cover_service import attach_cover_from_url, generate_random_color
from api.services.generation import (
    SongGenerationRequest,
    SongGenerationResult,
    get_song_generator,
)

logger = logging.getLogger(__name__)


class SongGenerationService:
    """Coordinate generation requests using a pluggable strategy."""

    def submit_generation(self, generation_request):
        strategy = get_song_generator(generation_request.generator_strategy)
        result = strategy.generate(self._build_payload(generation_request))
        return self._apply_result(generation_request, result)

    def sync_generation_status(self, generation_request):
        strategy = get_song_generator(generation_request.generator_strategy)
        result = strategy.sync(generation_request)
        if not result:
            return generation_request.song
        return self._apply_result(generation_request, result)

    def store_generated_song(
        self,
        generation_request,
        audio_url: str,
        cover_image_url: str | None = None,
    ) -> Song:
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
                        "Failed to download cover image for GenerationRequest %s",
                        generation_request.id,
                    )

            if not song.cover_image:
                song.cover_color = generate_random_color()
                update_fields.append("cover_color")

            song.save(update_fields=update_fields)
            generation_request.mark_completed(song)
            return song

    def _apply_result(self, generation_request, result: SongGenerationResult):
        if result.task_id and generation_request.external_task_id != result.task_id:
            generation_request.external_task_id = result.task_id
            generation_request.save(update_fields=["external_task_id", "updated_at"])

        if result.status == "completed":
            if result.audio_url:
                return self.store_generated_song(
                    generation_request,
                    result.audio_url,
                    cover_image_url=result.image_url,
                )
            generation_request.mark_failed("Generation completed without an audio URL.")
            return generation_request.song

        if result.status == "failed":
            generation_request.mark_failed(result.error or "Unknown generation error.")

        return generation_request.song

    def _build_payload(self, generation_request) -> SongGenerationRequest:
        try:
            style = Genre(generation_request.genre).label
        except ValueError:
            style = generation_request.genre

        return SongGenerationRequest(
            title=generation_request.title,
            prompt=generation_request.description,
            style=style,
        )