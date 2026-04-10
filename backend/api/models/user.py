from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Represents a user of the music generation application.

    Extends AbstractUser to inherit authentication fields (username,
    email, password, etc.) and adds optional Google OAuth identity.
    """

    google_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return self.username
    