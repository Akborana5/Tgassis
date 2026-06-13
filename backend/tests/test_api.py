from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.storage import store

client = TestClient(app)


def test_search_returns_ranked_results():
    response = client.get("/search", params={"q": "avenger"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 1
    assert payload["items"][0]["title"] == "Avengers Endgame"


def test_movie_details_found():
    response = client.get("/movie/avengers-endgame-2019")
    assert response.status_code == 200
    assert response.json()["title"] == "Avengers Endgame"


def test_stream_supports_range_header(tmp_path: Path):
    sample = tmp_path / "sample.bin"
    sample.write_bytes(b"0123456789")

    item = store.get("avengers-endgame-2019")
    assert item is not None
    item.files[0].local_path = str(sample)
    store.upsert(item)

    response = client.get("/stream/avengers-endgame-2019", headers={"Range": "bytes=2-5"})
    assert response.status_code == 206
    assert response.content == b"2345"
    assert response.headers["content-range"] == "bytes 2-5/10"
