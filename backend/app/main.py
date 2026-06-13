from __future__ import annotations

from pathlib import Path

from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from starlette import status

from .indexer import indexer
from .models import AdminActionResponse, MediaFile, MediaType
from .search import search_service
from .storage import store
from .streaming import file_chunk_iterator, parse_range, telegram_chunk_iterator
from .workers import worker_pool
from .tmdb import tmdb_client
from .config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await worker_pool.initialize()
    task = asyncio.create_task(indexer.run_forever())
    yield
    task.cancel()
    await worker_pool.close()

app = FastAPI(title="Telegram Media Search + Streaming API", version="0.1.0", lifespan=lifespan)


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
async def thumb(media_id: str):
    item = store.get(media_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")
        
    poster_path = Path(item.poster) if item.poster else settings.thumbs_dir / f"{media_id}.jpg"
    
    if poster_path.exists():
        return FileResponse(poster_path)
        
    # Try TMDB
    poster_bytes = await tmdb_client.fetch_poster(item.title, item.year)
    if poster_bytes:
        poster_path.write_bytes(poster_bytes)
        # Update item poster reference if it wasn't set
        if not item.poster:
            item.poster = str(poster_path)
            store.upsert(item)
        return FileResponse(poster_path)

    placeholder = {"id": media_id, "title": item.title, "placeholder": True}
    return JSONResponse(content=placeholder)



def _resolve_file(media_id: str) -> MediaFile:
    item = store.get(media_id)
    if not item or not item.files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No files available")
    return item.files[0]

@app.get("/stream/{media_id}")
async def stream(media_id: str, range_header: str | None = Header(None, alias="Range")):
    file_ref = _resolve_file(media_id)
    media_type = file_ref.mime_type or "application/octet-stream"
    
    if file_ref.local_path and Path(file_ref.local_path).exists():
        path = Path(file_ref.local_path)
        file_size = path.stat().st_size
        byte_range = parse_range(range_header, file_size)
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
            "Content-Length": str(byte_range.end - byte_range.start + 1),
        }
        code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
        return StreamingResponse(file_chunk_iterator(path, byte_range), status_code=code, headers=headers, media_type=media_type)
        
    # Proxy from Telegram
    if not file_ref.size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size unknown, cannot stream")
        
    worker = await worker_pool.next_worker()
    if not worker:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No active Telegram workers")
        
    file_size = file_ref.size
    byte_range = parse_range(range_header, file_size)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
        "Content-Length": str(byte_range.end - byte_range.start + 1),
    }
    code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
    
    return StreamingResponse(
        telegram_chunk_iterator(worker.client, file_ref.telegram_channel, file_ref.message_id, byte_range),
        status_code=code, 
        headers=headers, 
        media_type=media_type
    )

@app.get("/download/{media_id}")
async def download(media_id: str, range_header: str | None = Header(None, alias="Range")):
    file_ref = _resolve_file(media_id)
    media_type = file_ref.mime_type or "application/octet-stream"
    filename = file_ref.filename or "download"
    
    if file_ref.local_path and Path(file_ref.local_path).exists():
        path = Path(file_ref.local_path)
        file_size = path.stat().st_size
        byte_range = parse_range(range_header, file_size)
        headers = {
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
            "Content-Length": str(byte_range.end - byte_range.start + 1),
            "Content-Disposition": f'attachment; filename="{filename}"',
        }
        code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
        return StreamingResponse(file_chunk_iterator(path, byte_range), status_code=code, headers=headers, media_type=media_type)

    if not file_ref.size:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size unknown")
        
    worker = await worker_pool.next_worker()
    if not worker:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="No active Telegram workers")
        
    file_size = file_ref.size
    byte_range = parse_range(range_header, file_size)
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {byte_range.start}-{byte_range.end}/{file_size}",
        "Content-Length": str(byte_range.end - byte_range.start + 1),
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    code = status.HTTP_206_PARTIAL_CONTENT if range_header else status.HTTP_200_OK
    
    return StreamingResponse(
        telegram_chunk_iterator(worker.client, file_ref.telegram_channel, file_ref.message_id, byte_range),
        status_code=code, 
        headers=headers, 
        media_type=media_type
    )
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
