import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    max_pages: int = int(os.getenv("MAX_PAGES", "100"))
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "uploads"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "outputs"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.output_dir.mkdir(parents=True, exist_ok=True)