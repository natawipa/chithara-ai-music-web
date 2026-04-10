import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class SunoService:
    """Encapsulates all communication with the external Suno API.

    All outbound HTTP calls live here; no other layer should talk to Suno directly.
    """

    def __init__(self) -> None:
        self.base_url = settings.SUNO_API_BASE_URL.rstrip("/")
        # Reuse a single session for connection pooling and shared headers
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {settings.SUNO_API_KEY}",
                "Content-Type": "application/json",
            }
        )

    def generate_song(self, data: dict) -> str:
        """Submit a generation request to Suno and return the task ID.

        Only the required Suno fields are included in the payload.

        Args:
            data: dict with keys ``title``, ``prompt``, ``style``.

        Returns:
            The ``taskId`` string assigned by Suno.

        Raises:
            requests.HTTPError: if Suno responds with a non-2xx status.
            ValueError: if required fields are missing from ``data``.
        """
        for required_key in ("title", "prompt", "style"):
            if not data.get(required_key):
                raise ValueError(f"Missing required field: {required_key}")

        payload = {
            "customMode": True,
            "instrumental": False,
            "model": "V5",
            "callBackUrl": settings.SUNO_CALLBACK_URL,
            "prompt": data["prompt"],
            "style": data["style"],
            "title": data["title"],
        }
        response = self._session.post(
            f"{self.base_url}/generate",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        body = response.json()
        task_id = (body.get("data") or {}).get("taskId")
        if not task_id:
            raise ValueError("Suno response did not include data.taskId")
        return task_id

    def get_status(self, task_id: str) -> dict:
        """Poll Suno for the current status of a generation task.

        Args:
            task_id: The Suno task ID returned by ``generate_song``.

        Returns:
            Normalised dict::

                {
                    "status":    "processing" | "completed" | "failed",
                    "audio_url": str | None,
                    "error":     str | None,
                }

        Raises:
            requests.HTTPError: if Suno responds with a non-2xx status.
        """
        response = self._session.get(
            f"{self.base_url}/generate/{task_id}",
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json()

        # Normalise Suno's response envelope into a stable internal shape.
        # Suno wraps results under a "data" key; clips live in data["data"].
        data = raw.get("data", {})
        suno_status = data.get("status", "processing").lower()

        audio_url = None
        clips = data.get("data") or []
        if clips and isinstance(clips, list):
            audio_url = clips[0].get("audio_url") or clips[0].get("audioUrl")

        error = data.get("errorMessage") or data.get("error")

        # Map Suno status vocabulary to our internal vocabulary
        if suno_status in ("success", "complete", "completed"):
            status = "completed"
        elif suno_status in ("error", "fail", "failed"):
            status = "failed"
        else:
            status = "processing"

        return {"status": status, "audio_url": audio_url, "error": error}

    def get_credit(self) -> dict:
        """Return the remaining API credit information from Suno.

        Returns:
            Raw response dict from Suno with credit details.

        Raises:
            requests.HTTPError: if Suno responds with a non-2xx status.
        """
        response = self._session.get(
            f"{self.base_url}/generate/credit",
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
