from django.db import models


class Song(models.Model):
    """
    Represents a generated song.

    Stores metadata such as title, creator, genre, and audio file.
    Linked to the GenerationRequest for traceability and auditing.
    """
