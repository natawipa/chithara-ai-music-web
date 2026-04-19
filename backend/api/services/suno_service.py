import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class InsufficientCreditError(Exception):
    """Raised when Suno reports zero remaining credits."""


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

    @staticmethod
    def _extract_task_id(body: dict) -> str | None:
        """Return a task ID from known Suno response envelopes."""
        data = body.get("data")
        if isinstance(data, dict):
            return (
                data.get("taskId")
                or data.get("task_id")
                or data.get("id")
            )

        return body.get("taskId") or body.get("task_id") or body.get("id")

    @staticmethod
    def _raise_for_api_error(body: dict) -> None:
        """Raise a domain exception when Suno reports an application-level error."""
        code = body.get("code")
        if code in (None, 200):
            return

        message = body.get("msg") or "Suno request failed"
        lowered_message = message.lower()
        if code == 429 or "insufficient" in lowered_message or "credit" in lowered_message:
            raise InsufficientCreditError(message)

        raise ValueError(message)

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

        remaining_credit = self.get_credit()
        if remaining_credit <= 0:
            raise InsufficientCreditError("Out of credit")

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
        self._raise_for_api_error(body)
        task_id = self._extract_task_id(body)
        if not task_id:
            logger.error("Unexpected Suno generate response: %s", body)
            raise ValueError("Suno response did not include a task ID")
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
                    "image_url": str | None,
                    "error":     str | None,
                }

        Raises:
            requests.HTTPError: if Suno responds with a non-2xx status.
        """
        response = self._session.get(
            f"{self.base_url}/generate/record-info",
            params={"taskId": task_id},
            timeout=30,
        )
        response.raise_for_status()
        raw = response.json()
        self._raise_for_api_error(raw)

        data = raw.get("data") if isinstance(raw.get("data"), dict) else {}
        response_data = data.get("response") if isinstance(data.get("response"), dict) else {}

        suno_status = str(data.get("status") or response_data.get("status") or "PENDING").upper()

        audio_url = None
        image_url = None
        clips = response_data.get("sunoData") or data.get("data") or []
        if clips and isinstance(clips, list):
            audio_url = (
                clips[0].get("audio_url")
                or clips[0].get("audioUrl")
                or clips[0].get("source_audio_url")
                or clips[0].get("sourceAudioUrl")
            )
            image_url = (
                clips[0].get("image_url")
                or clips[0].get("imageUrl")
                or clips[0].get("source_image_url")
                or clips[0].get("sourceImageUrl")
            )

        error = data.get("errorMessage") or data.get("error") or raw.get("msg")

        # Map Suno status vocabulary to our internal vocabulary
        if suno_status in ("SUCCESS", "COMPLETE", "COMPLETED"):
            status = "completed"
        elif suno_status in (
            "CREATE_TASK_FAILED",
            "GENERATE_AUDIO_FAILED",
            "CALLBACK_EXCEPTION",
            "SENSITIVE_WORD_ERROR",
            "ERROR",
            "FAIL",
            "FAILED",
        ):
            status = "failed"
        else:
            status = "processing"

        return {
            "status": status,
            "audio_url": audio_url,
            "image_url": image_url,
            "error": error,
        }

    def get_credit(self) -> int:
        """Return the remaining Suno credit as an integer.

        Returns:
            Remaining credit value.

        Raises:
            requests.HTTPError: if Suno responds with a non-200 status.
            ValueError: if Suno returns an unexpected response envelope.
        """
        response = self._session.get(
            f"{self.base_url}/generate/credit",
            timeout=15,
        )
        if response.status_code != 200:
            raise requests.HTTPError(
                f"Unexpected status from Suno credit API: {response.status_code}",
                response=response,
            )

        body = response.json()
        self._raise_for_api_error(body)

        credit = body.get("data")
        if credit is None:
            raise ValueError("Suno credit response did not include data")

        try:
            return int(credit)
        except (TypeError, ValueError) as exc:
            raise ValueError("Suno credit response data is not a valid integer") from exc
