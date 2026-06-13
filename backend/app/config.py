from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    data_dir: Path = Path(__file__).resolve().parents[1] / "data"
    database_path: Path = data_dir / "database.json"
    thumbs_dir: Path = data_dir / "thumbs"
    cache_dir: Path = data_dir / "cache"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.thumbs_dir.mkdir(parents=True, exist_ok=True)
settings.cache_dir.mkdir(parents=True, exist_ok=True)
