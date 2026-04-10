from django.conf import settings
from django.db import models

from .enums import Genre, Occasion, PrivacyLevel, Tone


class Song(models.Model):
    """
    Represents a generated song.

    Stores metadata such as title, creator, genre, and audio file.
    Linked to the GenerationRequest for traceability and auditing.
    """

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    genre = models.CharField(max_length=50, choices=Genre.choices)
    tone = models.CharField(max_length=50, choices=Tone.choices)
    occasion = models.CharField(max_length=50, choices=Occasion.choices)
    audio_file = models.URLField(max_length=2048)
    privacy_level = models.CharField(
        max_length=10,
        choices=PrivacyLevel.choices,
        default=PrivacyLevel.PRIVATE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="songs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.user})"
