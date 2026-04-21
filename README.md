# Chithara — AI Music Generation

Chithara is a full-stack web application for AI-powered music generation, integrating with Suno's AI to create songs on demand. Users can generate new tracks and manage their personal music library.

**Backend:** Django REST API — music generation, status polling, and song management.  
**Frontend:** Vue 3 SPA — generation UI, song library, and playback.


## Project Structure

```
chithara-ai-music-web/
├── backend/    # Django REST API
└── frontend/   # Vue 3 single-page app
```


## Getting Started

### Prerequisites

- Python 3.x and pip
- Node.js and npm


### Backend Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/natawipa/chithara-ai-music-web
    cd chithara-ai-music-web/backend
    ```

2. **Create and activate a virtual environment**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4. **Configure environment variables**

    Create a `.env` file in the `backend/` directory:
    ```env
    DJANGO_SECRET_KEY=your-secret-key
    DEBUG=True
    GENERATOR_STRATEGY=suno
    SUNO_API_KEY=your-suno-api-key
    POSTGRES_DB=musicdb
    POSTGRES_USER=musicuser
    POSTGRES_PASSWORD=your-strong-db-password-here
    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    DATABASE_URL=postgresql://musicuser:your-strong-db-password-here@localhost:5432/musicdb
    MOCK_SONG_AUDIO_URL=https://example.com/mock/generated-song.mp3
    ```
    > The backend loads `.env` automatically if present. Never commit this file to version control.

5. **Start PostgreSQL**
    ```bash
    docker compose up -d db
    ```

6. **Apply database migrations**
    ```bash
    python3 manage.py migrate
    ```

7. **Create a superuser**
    ```bash
    python3 manage.py createsuperuser
    ```

8. **Start the development server**
    ```bash
    python3 manage.py runserver
    ```

The API will be available at `http://127.0.0.1:8000/`.  
The Django admin panel is at `http://127.0.0.1:8000/admin/` — log in with your superuser account to manage users, songs, and generation requests.


### Frontend Setup

1. **Install dependencies**
    ```bash
    cd ../frontend
    npm install
    ```

2. **Start the development server**
    ```bash
    npm run dev
    ```

The frontend will be available at the URL shown in your terminal (typically `http://localhost:5173/`).

> **Note:** Make sure the backend server is running before using the frontend, as it relies on the Django API for music generation and song data.


## Exercise 4

### Implemented Strategies

- `mock`: offline deterministic strategy that completes immediately and returns a fixed audio URL.
- `suno`: external strategy that submits a task to Suno, stores `external_task_id`, and polls Suno for status updates.

### Run in Mock Mode

Set the following in `backend/.env`:

```env
GENERATOR_STRATEGY=mock
MOCK_SONG_AUDIO_URL=https://example.com/mock/generated-song.mp3
```

Then start the backend normally:

```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver
```

Expected behavior:

```json
POST /api/generate/
{
    "id": 1,
    "status": "COMPLETED",
    "generator_strategy": "mock",
    "external_task_id": null
}
```

### Run in Suno Mode

Set the following in `backend/.env`:

```env
GENERATOR_STRATEGY=suno
SUNO_API_KEY=your-suno-api-key
SUNO_API_BASE_URL=https://api.sunoapi.org/api/v1
SUNO_CALLBACK_URL=http://localhost:8000/api/suno/callback/
```

Then run the backend:

```bash
cd backend
python3 manage.py migrate
python3 manage.py runserver
```

Expected behavior after submission:

```json
POST /api/generate/
{
    "id": 1,
    "status": "PROCESSING",
    "generator_strategy": "suno",
    "external_task_id": "task_abc123"
}
```

Later status polling returns the same request with either a completed song or an error:

```json
GET /api/generate/1/status/
{
    "id": 1,
    "status": "COMPLETED",
    "generator_strategy": "suno",
    "external_task_id": "task_abc123",
    "song": {
        "id": 1,
        "title": "My Song",
        "audio_file": "https://...",
        "cover_image": null,
        "cover_color": "#6E95B2",
        "genre": "POP",
        "tone": "HAPPY",
        "occasion": "PARTY",
        "privacy_level": "PRIVATE",
        "created_at": "2026-04-20T10:15:00+00:00"
    },
    "error": null
}
```

### Where to Put the Suno API Key

Put `SUNO_API_KEY` only in `backend/.env`. Do not commit real API keys to the repository.

### Minimal Demonstration

- Mock mode demonstration: generation completes immediately with `generator_strategy="mock"` and no external task ID.
- Suno mode demonstration: generation returns `external_task_id`, then the status endpoint retrieves Suno progress and final song details.


## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vite |
| Backend | Django, Django REST Framework |
| AI Integration | Suno API |
| Database | PostgreSQL |