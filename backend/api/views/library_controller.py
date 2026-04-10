"""
Handles querying user song library.

- List user songs
- Search songs by title
- Filter songs (genre, tone, occasion)
- Pagination on all views
"""

import logging

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from api.decorators import json_login_required
from api.models import Song

logger = logging.getLogger(__name__)

_DEFAULT_PAGE_SIZE = 20
_MAX_PAGE_SIZE = 100


# Internal helpers
def _paginate(queryset, request) -> dict:
    """Apply pagination query params and return a serialised page dict.

    Args:
        queryset: A Song queryset (may already be filtered).
        request:  The current HttpRequest (reads ``page`` and ``page_size``).

    Returns:
        { count, page, page_count, results }
    """
    try:
        page_size = min(
            int(request.GET.get("page_size", _DEFAULT_PAGE_SIZE)),
            _MAX_PAGE_SIZE,
        )
    except (ValueError, TypeError):
        page_size = _DEFAULT_PAGE_SIZE

    try:
        page_number = int(request.GET.get("page", 1))
    except (ValueError, TypeError):
        page_number = 1

    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page_number)

    results = [
        {
            "id": song.id,
            "title": song.title,
            "genre": song.genre,
            "tone": song.tone,
            "occasion": song.occasion,
            "audio_file": song.audio_file,
            "privacy_level": song.privacy_level,
            "created_at": song.created_at.isoformat(),
        }
        for song in page_obj
    ]

    return {
        "count": paginator.count,
        "page": page_obj.number,
        "page_count": paginator.num_pages,
        "results": results,
    }


# Views
@json_login_required
@require_GET
def list_songs(request):
    """Return a paginated list of all songs owned by the authenticated user.

    GET /api/songs/

    Query parameters:
        page      — 1-based page number (default: 1)
        page_size — results per page (default: 20, max: 100)

    Returns:
        200 { count, page, page_count, results }
        401 when unauthenticated.
    """
    songs = Song.objects.filter(user=request.user)
    return JsonResponse(_paginate(songs, request))


@json_login_required
@require_GET
def filter_songs(request):
    """Return songs filtered by genre, tone, and/or occasion.

    GET /api/songs/filter/

    Query parameters:
        genre     — e.g. "CLASSICAL", "HIP_HOP"
        tone      — e.g. "CALM", "ENERGETIC"
        occasion  — e.g. "BIRTHDAY", "WORKOUT"
        page, page_size — pagination

    At least one filter parameter should be provided; results are not
    restricted to public songs — users see only their own library.

    Returns:
        200 { count, page, page_count, results }
        401 when unauthenticated.
    """
    songs = Song.objects.filter(user=request.user)

    genre = request.GET.get("genre", "").strip().upper()
    tone = request.GET.get("tone", "").strip().upper()
    occasion = request.GET.get("occasion", "").strip().upper()

    if genre:
        songs = songs.filter(genre=genre)
    if tone:
        songs = songs.filter(tone=tone)
    if occasion:
        songs = songs.filter(occasion=occasion)

    return JsonResponse(_paginate(songs, request))


@json_login_required
@require_GET
def search_songs(request):
    """Search songs by title keyword (case-insensitive).

    GET /api/songs/search/

    Query parameters:
        q         — keyword to search in song titles (required)
        page, page_size — pagination

    Returns:
        200 { count, page, page_count, results }
        400 when the ``q`` parameter is missing or blank.
        401 when unauthenticated.
    """
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"error": "Query parameter 'q' is required."}, status=400)

    songs = Song.objects.filter(user=request.user, title__icontains=query)
    return JsonResponse(_paginate(songs, request))
