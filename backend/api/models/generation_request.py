from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .enums import GenerationStatus, Genre, Occasion, Tone


class GenerationRequest(models.Model):
    """
    Represents a user's music generation request.

    Stores input parameters, request status, and associated user.
    Acts as a log for tracking usage and analyzing behavior.
    Allows failed requests to be edited and retried without creating a new record.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generation_requests",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    genre = models.CharField(max_length=50, choices=Genre.choices)
    tone = models.CharField(max_length=50, choices=Tone.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    status = models.CharField(
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PROCESSING,
    )
    error_message = models.TextField(blank=True, default="")
    song = models.OneToOneField(
        "Song",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_request",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"GenerationRequest({self.id}) — {self.title} [{self.status}]"

    # State transitions
    def mark_completed(self, song) -> None:
        """Transition to COMPLETED and attach the resulting song."""
        if self.status in (GenerationStatus.COMPLETED, GenerationStatus.CANCELLED):
            raise ValidationError(
                f"Cannot complete a request that is already {self.status}."
            )
        self.song = song
        self.status = GenerationStatus.COMPLETED
        self.save(update_fields=["song", "status", "updated_at"])

    def mark_failed(self, error_message: str) -> None:
        """Transition to FAILED and record the error message."""
        self.status = GenerationStatus.FAILED
        self.error_message = error_message
        self.save(update_fields=["status", "error_message", "updated_at"])

    def cancel(self) -> None:
        """Transition to CANCELLED."""
        if self.status == GenerationStatus.COMPLETED:
            raise ValidationError("Cannot cancel a request that is already completed.")
        self.status = GenerationStatus.CANCELLED
        self.save(update_fields=["status", "updated_at"])
    