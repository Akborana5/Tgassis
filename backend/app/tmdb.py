import os
import aiohttp
import asyncio
import logging
from pathlib import Path
from .config import settings

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"

    async def fetch_poster(self, title: str, year: int | None = None) -> bytes | None:
        if not self.api_key:
            return None
        
        async with aiohttp.ClientSession() as session:
            try:
                params = {"api_key": self.api_key, "query": title}
                if year:
                    params["year"] = str(year)
                    
                async with session.get(f"{self.base_url}/search/multi", params=params) as resp:
                    if resp.status != 200:
                        return None
                    data = await resp.json()
                    
                results = data.get("results", [])
                if not results:
                    return None
                    
                poster_path = results[0].get("poster_path")
                if not poster_path:
                    return None
                    
                image_url = f"{self.image_base_url}{poster_path}"
                async with session.get(image_url) as resp:
                    if resp.status == 200:
                        return await resp.read()
                        
            except Exception as e:
                logger.error(f"TMDB fetch error: {e}")
                
        return None

tmdb_client = TMDBClient()
