# Chithara — AI Music Generation

Chithara is a full-stack web application for AI-powered music generation using the Suno API. Users can generate songs from prompts, monitor generation progress, and manage a personal music library through a modern web interface.

**Backend:** Django REST API for generation workflows, status polling, and song management  
**Frontend:** Vue 3 SPA for generation UI, and playback


## Features

- AI-powered song generation with Suno
- Personal music library management
- Song playback in browser
- Real-time generation status polling
- Pluggable generation strategies (`mock` and `suno`)
- Full-stack architecture with Django + Vue


## Project Structure

```bash
chithara-ai-music-web/
├── backend/      # Django REST API
└── frontend/     # Vue 3 single-page app
```


## Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | Vue 3, Vite |
| Backend | Django, Django REST Framework |
| AI Integration | Suno API |
| Database | PostgreSQL |


# Getting Started

## Prerequisites

- Python 3.x
- pip
- Node.js + npm
- PostgreSQL


# Backend Setup

## 1. Clone repository

```bash
git clone https://github.com/natawipa/chithara-ai-music-web.git
cd chithara-ai-music-web/backend
```

## 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure environment variables

Create a `.env` file inside `backend/`:

```env
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True

GENERATOR_STRATEGY=suno  # or "mock" for testing without real API calls
SUNO_API_KEY=your-suno-api-key
SUNO_API_BASE_URL=https://api.sunoapi.org/api/v1
SUNO_CALLBACK_URL=http://localhost:8000/api/suno/callback/

POSTGRES_DB=musicdb
POSTGRES_USER=musicuser
POSTGRES_PASSWORD=your-db-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

DATABASE_URL=postgresql://musicuser:your-db-password@localhost:5432/musicdb

MOCK_SONG_AUDIO_URL=https://example.com/mock/generated-song.mp3
```

> Do not commit `.env` or real API keys.

---

## 5. Start PostgreSQL with Docker

From the project root:

```bash
cd ..
docker compose up -d db
```

This starts a PostgreSQL container for the Django app.

Verify database is running:

```bash
docker ps
```

---

## 6. Run migrations

```bash
python manage.py migrate
```

## 7. Create superuser

```bash
python manage.py createsuperuser
```

## 8. Start backend server

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000/
```

Admin:

```text
http://127.0.0.1:8000/admin/
```


# Frontend Setup

```bash
cd ../frontend
npm install
npm run dev
```

Frontend usually runs at:

```text
http://localhost:5173/
```

Make sure backend is running before using frontend.


# Generation Strategies

## Mock Strategy

Useful for development/testing.

Set:

```env
GENERATOR_STRATEGY=mock
MOCK_SONG_AUDIO_URL=https://example.com/mock/generated-song.mp3
```

Run backend normally:

```bash
python manage.py migrate
python manage.py runserver
```

Example response:

```json
POST /api/generate/
{
  "id": 1,
  "status": "COMPLETED",
  "generator_strategy": "mock",
  "external_task_id": null
}
```


## Suno Strategy

Set:

```env
GENERATOR_STRATEGY=suno
SUNO_API_KEY=your-suno-api-key
SUNO_API_BASE_URL=https://api.sunoapi.org/api/v1
SUNO_CALLBACK_URL=http://localhost:8000/api/suno/callback/
```

Example generation request:

```json
POST /api/generate/
{
  "id": 1,
  "status": "PROCESSING",
  "generator_strategy": "suno",
  "external_task_id": "task_abc123"
}
```

Polling:

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