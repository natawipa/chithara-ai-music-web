from django.db import models


class GenerationStatus(models.TextChoices):
    CANCELLED = "CANCELLED", "Cancelled"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"
    PROCESSING = "PROCESSING", "Processing"


class Genre(models.TextChoices):
    CLASSICAL = "CLASSICAL", "Classical"
    COMEDY = "COMEDY", "Comedy"
    COUNTRY = "COUNTRY", "Country"
    EASY_LISTENING = "EASY_LISTENING", "Easy Listening"
    ELECTRONIC = "ELECTRONIC", "Electronic"
    FOLK = "FOLK", "Folk"
    HIP_HOP = "HIP_HOP", "Hip-Hop"
    JAZZ = "JAZZ", "Jazz"
    LATIN = "LATIN", "Latin"
    POP = "POP", "Pop"
    RNB_SOUL = "RNB_SOUL", "R&B and Soul"
    ROCK = "ROCK", "Rock"


class Tone(models.TextChoices):
    CALM = "CALM", "Calm"
    ENERGETIC = "ENERGETIC", "Energetic"
    HAPPY = "HAPPY", "Happy"
    ROMANTIC = "ROMANTIC", "Romantic"
    SAD = "SAD", "Sad"


class Occasion(models.TextChoices):
    BIRTHDAY = "BIRTHDAY", "Birthday"
    FESTIVE = "FESTIVE", "Festive"
    PARTY = "PARTY", "Party"
    RELAX = "RELAX", "Relax"
    WEDDING = "WEDDING", "Wedding"
    WORKOUT = "WORKOUT", "Workout"


class PrivacyLevel(models.TextChoices):
    PRIVATE = "PRIVATE", "Private"
    PUBLIC = "PUBLIC", "Public"