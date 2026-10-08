import re
from pathlib import Path
from uuid import uuid4


def validate_pdf_filename(filename: str) -> None:
    if not filename or Path(filename).suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are allowed.")


def create_safe_path(directory: Path, filename: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    return directory / f"{uuid4().hex}_{safe_name}"