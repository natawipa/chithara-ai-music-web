from django.db import models


class User(models.Model):
    """
    Represents a user of the music generation application.

    Stores basic user information and is linked to generation requests
    and created songs.
    """
    