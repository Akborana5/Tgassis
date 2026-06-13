import os
import logging
from pathlib import Path
from huggingface_hub import HfApi
from .config import settings

logger = logging.getLogger(__name__)

class HuggingFaceSync:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        self.repo_id = os.getenv("HF_REPO_ID")
        self.api = HfApi(token=self.token) if self.token else None

    def sync_database_up(self):
        if not self.api or not self.repo_id:
            return
        try:
            self.api.upload_file(
                path_or_fileobj=str(settings.database_path),
                path_in_repo="database.json",
                repo_id=self.repo_id,
                repo_type="dataset",
            )
            logger.info("Synchronized database.json to HuggingFace Datasets.")
        except Exception as e:
            logger.error(f"Failed to sync up to HF: {e}")

    def sync_database_down(self):
        if not self.api or not self.repo_id:
            return
        try:
            from huggingface_hub import hf_hub_download
            downloaded = hf_hub_download(
                repo_id=self.repo_id,
                filename="database.json",
                repo_type="dataset",
                token=self.token
            )
            import shutil
            shutil.copy(downloaded, settings.database_path)
            logger.info("Downloaded latest database.json from HuggingFace.")
        except Exception as e:
            logger.error(f"Failed to sync down from HF: {e}")

hf_sync = HuggingFaceSync()
