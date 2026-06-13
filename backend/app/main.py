from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from starlette import status

from .models import AdminActionResponse, MediaType
from .search import search_service
from .storage import store
from .streaming import file_chunk_iterator, parse_range
from .workers import worker_pool

app = FastAPI(title="Telegram Media Search + Streaming API", version="0.1.0")


@app.get("/search")
def search_media(q: str = Query("", min_length=0), page: int = 1, page_size: int = 20):
    return search_service.search(q, store.all(), page=page, page_size=min(page_size, 100))


@app.get("/movie/{media_id}")
def movie_details(media_id: str):
    item = store.get(media_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
    return item


@app.get("/recent")
def recent_media(limit: int = 20):
    return store.all()[:limit]


@app.get("/anime")
def anime_items(limit: int = 20):
    return store.by_type(MediaType.anime)[:limit]


@app.get("/movies")
def movie_items(limit: int = 20):
    return store.by_type(MediaType.movie)[:limit]


@app.get("/series")
def series_items(limit: int = 20):
    return store.by_type(MediaType.series)[:limit]


@app.get("/thumb/{media_id}")
def thumb(media_id: str):
    item = store.get(media_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
    if item.poster and Path(item.poster).exists():
        return FileResponse(item.poster)
    placeholder = {"id": media_id, "title": item.title, "placeholder": True}
    return JSONResponse(content=placeholder)


def _resolve_file(media_id: str) -> tuple[Path, str]:
    item = store.get(media_id)
    if not item or not item.files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No files available")
    file_ref = item.files[0]
    if not file_ref.local_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File proxy path is not configured; Telegram links are intentionally hidden.",
        )
    path = Path(file_ref.local_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return path, file_ref.mime_type or "application/octet-stream"


@app.get("/stream/{media_id}")
def stream(media_id: str, range_header: str | None = Header(None, alias="Range")):
    path, media_type = _resolve_file(media_id)
    file_size = path.stat().st_size
    byte_range = parse_range(range_header, file_size)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
        "Content-Length": str(byte_range.end - byte_range.start + 1),
    }
    code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
    return StreamingResponse(file_chunk_iterator(path, byte_range), status_code=code, headers=headers, media_type=media_type)


@app.get("/download/{media_id}")
def download(media_id: str, range_header: str | None = Header(None, alias="Range")):
    path, media_type = _resolve_file(media_id)
    file_size = path.stat().st_size
    byte_range = parse_range(range_header, file_size)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
        "Content-Length": str(byte_range.end - byte_range.start + 1),
        "Content-Disposition": f'attachment; filename="{path.name}"',
    }
    code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
    return StreamingResponse(file_chunk_iterator(path, byte_range), status_code=code, headers=headers, media_type=media_type)


@app.post("/admin/rebuild", response_model=AdminActionResponse)
async def admin_rebuild():
    worker = await worker_pool.next_worker()
    return AdminActionResponse(status="queued", detail=f"Search rebuild queued on {worker.name}")


@app.post("/admin/rescan", response_model=AdminActionResponse)
async def admin_rescan():
    worker = await worker_pool.next_worker()
    return AdminActionResponse(status="queued", detail=f"Channel rescan queued on {worker.name}")


@app.get("/admin/workers")
async def workers_status():
    return {"workers": await worker_pool.status()}
