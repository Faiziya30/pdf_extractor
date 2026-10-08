import logging
import time
from pathlib import Path
from typing import Dict
from uuid import uuid4

from fastapi import UploadFile

from app.config.settings import Settings, settings
from app.exceptions.document_exceptions import DocumentError, DocumentNotFoundError, FileTooLargeError
from app.models.document_model import DocumentRecord
from app.services.pdf_service import PdfService
from app.utils.file_utils import create_safe_path, validate_pdf_filename

logger = logging.getLogger(__name__)


class DocumentController:
    def __init__(self, app_settings: Settings = settings, pdf_service: PdfService | None = None):
        self.settings = app_settings
        self.pdf_service = pdf_service or PdfService()
        self.documents: Dict[str, DocumentRecord] = {}

    async def upload(self, file: UploadFile):
        filename = file.filename or ""
        try:
            validate_pdf_filename(filename)
        except ValueError as exc:
            raise DocumentError("UNSUPPORTED_FILE", str(exc), 400) from exc
        if file.content_type and file.content_type not in {"application/pdf", "application/octet-stream"}:
            raise DocumentError("UNSUPPORTED_FILE", "The uploaded file must have PDF content.", 400)

        document_id = uuid4().hex
        path = create_safe_path(self.settings.upload_dir, filename)
        size = 0
        logger.info("Upload received: document_id=%s filename=%s", document_id, filename)
        try:
            with path.open("wb") as target:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > self.settings.max_file_size_bytes:
                        raise FileTooLargeError(self.settings.max_file_size_mb)
                    target.write(chunk)
            if size == 0:
                raise DocumentError("EMPTY_FILE", "The uploaded file is empty.", 400)
            start = time.perf_counter()
            logger.info("Processing started: document_id=%s", document_id)
            data = self.pdf_service.process(path, document_id, filename, size, self.settings.max_pages)
            duration_ms = round((time.perf_counter() - start) * 1000)
            data["processing_time_ms"] = duration_ms
            self.documents[document_id] = DocumentRecord(document_id, filename, size, path, data)
            logger.info("Processing completed: document_id=%s duration_ms=%s", document_id, duration_ms)
            return data
        except Exception:
            if path.exists():
                path.unlink()
            logger.exception("Document processing failed: document_id=%s", document_id)
            raise

    def get(self, document_id: str) -> DocumentRecord:
        document = self.documents.get(document_id)
        if not document:
            raise DocumentNotFoundError()
        return document

    def delete(self, document_id: str) -> None:
        document = self.get(document_id)
        self.documents.pop(document_id, None)
        if document.source_path.exists():
            document.source_path.unlink()