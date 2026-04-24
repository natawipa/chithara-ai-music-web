# Chithara — AI Music Generation

Chithara is a full-stack web application for AI-powered music generation using the Suno API.  
Users can generate songs from text prompts and manage a personal music library.

## Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | Vue 3, Vite, Tailwind CSS |
| Backend | Django 5, psycopg3 |
| Database | PostgreSQL 15 |
| AI | Suno API (pluggable strategies) |

## Table of Contents

1. Prerequisites  
2. Installation  
3. Database Setup  
4. Environment Configuration  
5. Running the Application  
6. Mock Song Generation  
7. API Overview  
8. Troubleshooting  
9. Project Structure

# 1. Prerequisites

Install:

- Python 3.11+
- Node.js 18+
- npm 9+
- PostgreSQL 15+
- Git

Check versions:

```bash
python3 --version
node --version
npm --version
psql --version
git --version
```

## Install PostgreSQL

### macOS

```bash
brew install postgresql@15
brew services start postgresql@15
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### Windows

Download and install:

https://www.postgresql.org/download/windows/

# 2. Installation

Clone repository:

```bash
git clone https://github.com/natawipa/chithara-ai-music-web.git
cd chithara-ai-music-web
```

## Create Python virtual environment

```bash
python3 -m venv .venv
```

Activate it:

Mac/Linux

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install backend dependencies:

```bash
pip install --upgrade pip
pip install -r backend/requirements.txt
```

Install frontend dependencies:

```bash
cd frontend
npm install
cd ..
```

# 3. Database Setup

Connect to PostgreSQL:

macOS:

```bash
psql postgres
```

Ubuntu:

```bash
sudo -u postgres psql
```

Create database and user:

```sql
CREATE USER musicuser WITH PASSWORD 'musicpassword';
CREATE DATABASE musicdb OWNER musicuser;
GRANT ALL PRIVILEGES ON DATABASE musicdb TO musicuser;
\q
```

Verify:

```bash
psql -U musicuser -d musicdb -c "\conninfo"
```

# 4. Environment Configuration

Copy example config:

```bash
cp backend/.env.example backend/.env
```

Edit:

```bash
backend/.env
```

Minimum configuration:

```env
DJANGO_SECRET_KEY=replace_me
POSTGRES_DB=musicdb
POSTGRES_USER=musicuser
POSTGRES_PASSWORD=musicpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

GENERATOR_STRATEGY=mock
```

Generate secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

Paste into:

```env
DJANGO_SECRET_KEY=your_generated_secret
```

# 5. Running the Application

## Run migrations

```bash
cd backend
python manage.py migrate
```

Optional admin user:

```bash
python manage.py createsuperuser
```

## Start backend

```bash
python manage.py runserver
```

Backend:

```text
http://127.0.0.1:8000
```

Open a second terminal:

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:5173
```

# 6. Mock Song Generation

Recommended for development:

```env
GENERATOR_STRATEGY=mock
MOCK_SONG_AUDIO_URL=https://example.com/mock-song.mp3
```

No Suno key required.

## Real Suno Integration

```env
GENERATOR_STRATEGY=suno
SUNO_API_KEY=your_api_key
```

# 7. API Overview

All endpoints begin with:

```text
/api/
```

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register/` | Register |
| POST | `/auth/login/` | Login |
| POST | `/auth/logout/` | Logout |
| GET | `/songs/` | List songs |
| POST | `/generate/` | Generate song |
| GET | `/generate/<id>/status/` | Poll generation |
| PATCH | `/songs/<id>/` | Update song |
| DELETE | `/songs/<id>/` | Delete song |
| GET | `/library/` | Public library |

# 8. Troubleshooting

## PostgreSQL connection refused

Start PostgreSQL:

Mac:

```bash
brew services start postgresql@15
```

Linux:

```bash
sudo systemctl start postgresql
```

## role "musicuser" does not exist

```sql
CREATE USER musicuser WITH PASSWORD 'musicpassword';
```

## database "musicdb" does not exist

```sql
CREATE DATABASE musicdb OWNER musicuser;
```

## Django not found

Activate venv:

```bash
source .venv/bin/activate
```

Reinstall dependencies:

```bash
pip install -r backend/requirements.txt
```

## Migration errors

Check `.env` values:

```env
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_HOST
```

# 9. Project Structure

```text
chithara-ai-music-web/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   └── views/
│   └── config/
│       └── settings.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── api/
│   └── package.json
│
└── README.md
```

## Development Workflow

Run backend:

```bash
cd backend
python manage.py runserver
```

Run frontend:

```bash
cd frontend
npm run dev
```

Open:

- Frontend: http://localhost:5173  
- Backend: http://127.0.0.1:8000