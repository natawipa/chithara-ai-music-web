import random

import requests
from django.core.files.base import ContentFile


def attach_cover_from_url(song, image_url: str, *, timeout: int = 30) -> bool:
    """Download a remote cover image and attach it to a Song.

    Returns True when the image is fetched and assigned successfully.
    """
    if not image_url:
        return False

    response = requests.get(image_url, timeout=timeout)
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "").lower()
    extension = ".jpg"
    if "png" in content_type:
        extension = ".png"
    elif "webp" in content_type:
        extension = ".webp"
    elif "gif" in content_type:
        extension = ".gif"

    filename = f"suno_cover_{song.user_id}_{song.id}{extension}"
    song.cover_image.save(filename, ContentFile(response.content), save=False)
    song.cover_color = ""
    return True


def generate_random_color() -> str:
    return f"#{random.randint(0, 0xFFFFFF):06X}"
