from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class DocumentRecord:
    document_id: str
    filename: str
    file_size: int
    source_path: Path
    data: Dict[str, Any]