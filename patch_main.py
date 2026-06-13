import re

with open('/home/runner/work/Tgassis/Tgassis/Akborana5/Tgassis/backend/app/main.py', 'r') as f:
    content = f.read()

# Replace _resolve_file and the route handlers
new_routing_code = """
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
"""

content = re.sub(r'def _resolve_file\(.*?(?=@app\.post\("/admin/rebuild")', new_routing_code, content, flags=re.DOTALL | re.MULTILINE)

with open('/home/runner/work/Tgassis/Tgassis/Akborana5/Tgassis/backend/app/main.py', 'w') as f:
    f.write(content)
