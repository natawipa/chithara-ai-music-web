from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from api.models.enums import GeneratorStrategy
from api.services.suno_service import SunoService


@dataclass(frozen=True)
class SongGenerationRequest:
    title: str
    prompt: str
    style: str


@dataclass(frozen=True)
class SongGenerationResult:
    status: str
    task_id: str | None = None
    audio_url: str | None = None
    image_url: str | None = None
    error: str | None = None
    metadata: dict = field(default_factory=dict)


class SongGeneratorStrategy(ABC):
    name: str

    @abstractmethod
    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        """Submit a song generation request and return a normalized result."""

    def sync(self, generation_request) -> SongGenerationResult | None:
        """Synchronize an existing generation request, if supported by the strategy."""
        return None


class MockSongGeneratorStrategy(SongGeneratorStrategy):
    name = GeneratorStrategy.MOCK

    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        return SongGenerationResult(
            status="completed",
            audio_url=settings.MOCK_SONG_AUDIO_URL,
            metadata={
                "provider": self.name,
                "title": request.title,
                "style": request.style,
            },
        )


class SunoSongGeneratorStrategy(SongGeneratorStrategy):
    name = GeneratorStrategy.SUNO

    def __init__(self, service: SunoService | None = None) -> None:
        self._service = service or SunoService()

    def generate(self, request: SongGenerationRequest) -> SongGenerationResult:
        task_id = self._service.generate_song(
            {
                "title": request.title,
                "prompt": request.prompt,
                "style": request.style,
            }
        )
        return SongGenerationResult(status="processing", task_id=task_id)

    def sync(self, generation_request) -> SongGenerationResult | None:
        task_id = generation_request.external_task_id
        if not task_id or generation_request.song_id:
            return None

        result = self._service.get_status(task_id)
        return SongGenerationResult(
            status=result.get("status") or "processing",
            task_id=task_id,
            audio_url=result.get("audio_url"),
            image_url=result.get("image_url"),
            error=result.get("error"),
            metadata={"provider": self.name},
        )


def get_song_generator(name: str | None = None) -> SongGeneratorStrategy:
    strategy_name = (name or settings.GENERATOR_STRATEGY).strip().lower()
    strategies = {
        GeneratorStrategy.MOCK: MockSongGeneratorStrategy,
        GeneratorStrategy.SUNO: SunoSongGeneratorStrategy,
    }
    strategy_class = strategies.get(strategy_name)
    if not strategy_class:
        supported = ", ".join(str(value) for value, _ in GeneratorStrategy.choices)
        raise ImproperlyConfigured(
            f"Unsupported GENERATOR_STRATEGY '{strategy_name}'. Expected one of: {supported}."
        )
    return strategy_class()