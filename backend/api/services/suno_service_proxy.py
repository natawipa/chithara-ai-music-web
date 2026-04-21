from api.services.generation_service import SongGenerationService


class SunoServiceProxy(SongGenerationService):
    """Backward-compatible alias for the generic generation service."""
