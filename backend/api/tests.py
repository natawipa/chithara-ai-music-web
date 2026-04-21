from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings

from api.models import GenerationRequest, Song, User
from api.models.enums import GeneratorStrategy, Genre, Occasion, Tone
from api.services.generation import (
    MockSongGeneratorStrategy,
    SongGenerationRequest,
    SunoSongGeneratorStrategy,
    get_song_generator,
)
from api.services.generation_service import SongGenerationService


class SongGenerationStrategyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="student", password="secret123")

    @override_settings(
        GENERATOR_STRATEGY="mock",
        MOCK_SONG_AUDIO_URL="https://example.com/mock-track.mp3",
    )
    def test_mock_strategy_completes_request_immediately(self):
        generation_request = GenerationRequest.objects.create(
            user=self.user,
            title="Mock Song",
            description="A deterministic offline song",
            genre=Genre.POP,
            tone=Tone.HAPPY,
            occasion=Occasion.PARTY,
            generator_strategy=GeneratorStrategy.MOCK,
        )

        SongGenerationService().submit_generation(generation_request)

        generation_request.refresh_from_db()
        self.assertEqual(generation_request.status, "COMPLETED")
        self.assertEqual(generation_request.generator_strategy, GeneratorStrategy.MOCK)
        self.assertEqual(generation_request.external_task_id, None)
        self.assertIsNotNone(generation_request.song)
        self.assertEqual(generation_request.song.audio_file, "https://example.com/mock-track.mp3")
        self.assertEqual(Song.objects.count(), 1)

    def test_suno_strategy_returns_task_id_and_syncs_status(self):
        class FakeSunoService:
            def generate_song(self, data):
                self.generated = data
                return "task-123"

            def get_status(self, task_id):
                return {
                    "status": "completed",
                    "audio_url": "https://example.com/suno-track.mp3",
                    "image_url": None,
                    "error": None,
                }

        strategy = SunoSongGeneratorStrategy(service=FakeSunoService())
        request_payload = SongGenerationRequest(
            title="Suno Song",
            prompt="A synthwave anthem",
            style="Electronic",
        )
        generation_request = GenerationRequest.objects.create(
            user=self.user,
            title="Suno Song",
            description="A synthwave anthem",
            genre=Genre.ELECTRONIC,
            tone=Tone.ENERGETIC,
            occasion=Occasion.PARTY,
            generator_strategy=GeneratorStrategy.SUNO,
            external_task_id="task-123",
        )

        submitted = strategy.generate(request_payload)
        synced = strategy.sync(generation_request)

        self.assertEqual(submitted.status, "processing")
        self.assertEqual(submitted.task_id, "task-123")
        self.assertEqual(synced.status, "completed")
        self.assertEqual(synced.audio_url, "https://example.com/suno-track.mp3")

    @override_settings(GENERATOR_STRATEGY="invalid")
    def test_invalid_strategy_setting_raises_error(self):
        with self.assertRaises(ImproperlyConfigured):
            get_song_generator()

    def test_factory_returns_mock_strategy(self):
        strategy = get_song_generator(GeneratorStrategy.MOCK)
        self.assertIsInstance(strategy, MockSongGeneratorStrategy)