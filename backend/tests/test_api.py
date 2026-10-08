import fitz
import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.controllers.document_controller import DocumentController
from app.main import app, document_controller


def make_pdf() -> bytes:
    document = fitz.open()
    document.set_metadata({"title": "Test Report", "author": "SmartPDF"})
    page = document.new_page()
    page.insert_text((72, 72), "1. Introduction", fontsize=20, fontname="hebo")
    page.insert_text((72, 110), "This is a body paragraph with useful document text.", fontsize=11)
    page.insert_text((72, 160), "1.1 Methodology", fontsize=16, fontname="hebo")
    page.insert_text((72, 200), "The method is described on this page.", fontsize=11)
    page = document.new_page()
    page.insert_text((72, 72), "2. Results", fontsize=20, fontname="hebo")
    page.insert_text((72, 110), "Results are available for review.", fontsize=11)
    content = document.tobytes()
    document.close()
    return content


@pytest.fixture(autouse=True)
def clean_documents():
    document_controller.documents.clear()
    yield
    for record in list(document_controller.documents.values()):
        if record.source_path.exists():
            record.source_path.unlink()
    document_controller.documents.clear()


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "SmartPDF API is running"}


def test_valid_upload_extracts_document_pages_metadata_and_headings():
    response = client.post("/api/documents/upload", files={"file": ("report.pdf", make_pdf(), "application/pdf")})
    payload = response.json()
    assert response.status_code == 200
    assert payload["document"]["metadata"]["title"] == "Test Report"
    assert payload["document"]["page_count"] == 2
    assert "body paragraph" in payload["pages"][0]["text"]
    assert any(item["text"] == "1.1 Methodology" and item["level"] == 2 for item in payload["outline"])
    assert all(0 <= item["confidence"] <= 1 for item in payload["outline"])


def test_invalid_file_is_rejected():
    response = client.post("/api/documents/upload", files={"file": ("notes.txt", b"not a pdf", "text/plain")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE"


def test_corrupted_pdf_is_rejected():
    response = client.post("/api/documents/upload", files={"file": ("broken.pdf", b"not a pdf", "application/pdf")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_PDF"


def test_document_not_found():
    response = client.get("/api/documents/missing")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_oversized_file():
    controller = DocumentController(Settings(max_file_size_mb=0, max_pages=100))
    file = type("Upload", (), {"filename": "large.pdf", "content_type": "application/pdf"})()

    async def upload(_size):
        return b"x"

    file.read = upload
    with pytest.raises(Exception) as error:
        import asyncio
        asyncio.run(controller.upload(file))
    assert getattr(error.value, "code", None) == "FILE_TOO_LARGE"