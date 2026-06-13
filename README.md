# Tgassis

Self-hosted Telegram media search + streaming stack.

## Services

- `backend/` FastAPI API for search, metadata, stream proxy, download proxy, and admin actions.
- `frontend/` Next.js UI for search and media details.

## Quick start (local)

```bash
docker compose up --build
```

- Backend: `http://localhost:8000/docs`
- Frontend: `http://localhost:3000`

## Backend development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest
```

## Frontend development

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` if backend is not at `http://localhost:8000`.
