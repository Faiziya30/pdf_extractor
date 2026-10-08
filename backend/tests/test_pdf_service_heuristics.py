import fitz
import pytest

from app.exceptions.document_exceptions import EmptyDocumentError
from app.services.pdf_service import PdfService


def make_adversarial_pdf(path):
    document = fitz.open()
    document.set_metadata({
        "title": "Smart Campus Energy Forecasting",
        "author": "Test Author",
        "subject": "Energy research",
        "creator": "Test Generator",
        "producer": "Test Producer",
        "creationDate": "D:20260101000000Z",
        "modDate": "D:20260102000000Z",
    })
    page = document.new_page()
    page.insert_text((170, 70), "Smart Campus Energy Forecasting 2026", fontsize=22, fontname="hebo")
    page.insert_text((170, 96), "A practical forecasting study", fontsize=12, fontname="heit")
    page.insert_text((72, 160), "1. Introduction", fontsize=16, fontname="hebo")
    page.insert_text((72, 190), "This paragraph explains the research context and motivation.", fontsize=11)
    page.insert_text((72, 240), "2. Methodology", fontsize=16, fontname="hebo")
    page.insert_text((90, 270), "2.1 Dataset", fontsize=13, fontname="hebo")
    page.insert_text((72, 320), "NOTE", fontsize=14, fontname="hebo")
    page.insert_text((72, 360), "Civil 290 208", fontsize=14, fontname="hebo")
    page.insert_text((72, 390), "2026 2050 1516 74.0%", fontsize=11)
    document.save(path)
    document.close()


def extract_fixture(tmp_path):
    path = tmp_path / "adversarial.pdf"
    make_adversarial_pdf(path)
    return PdfService().process(path, "test-id", path.name, path.stat().st_size, 100)


def test_metadata_extraction_returns_real_fields_and_dates(tmp_path):
    result = extract_fixture(tmp_path)
    metadata = result["document"]["metadata"]
    assert result["document"]["metadata_status"] == "available"
    assert metadata["title"] == "Smart Campus Energy Forecasting"
    assert metadata["author"] == "Test Author"
    assert metadata["creator"] == "Test Generator"
    assert metadata["creationDate"] == "D:20260101000000Z"
    assert metadata["modDate"] == "D:20260102000000Z"


def test_document_title_is_separate_from_outline(tmp_path):
    result = extract_fixture(tmp_path)
    outline_text = [heading["text"] for heading in result["outline"]]
    assert result["document"]["title"] == "Smart Campus Energy Forecasting 2026"
    assert result["document"]["title"] not in outline_text
    assert "A practical forecasting study" not in outline_text


def test_numbered_hierarchy_is_preserved(tmp_path):
    outline = extract_fixture(tmp_path)["outline"]
    levels = {heading["text"]: heading["level"] for heading in outline}
    assert levels["1. Introduction"] == 1
    assert levels["2. Methodology"] == 1
    assert levels["2.1 Dataset"] == 2


def test_table_and_numeric_rows_are_not_headings(tmp_path):
    outline_text = [heading["text"] for heading in extract_fixture(tmp_path)["outline"]]
    assert "Civil 290 208" not in outline_text
    assert "2026 2050 1516 74.0%" not in outline_text


def test_note_is_not_automatically_classified_as_heading(tmp_path):
    outline_text = [heading["text"] for heading in extract_fixture(tmp_path)["outline"]]
    assert "NOTE" not in outline_text


def test_image_only_pdf_reports_no_native_text(tmp_path):
    path = tmp_path / "image-only.pdf"
    document = fitz.open()
    document.new_page()
    document.save(path)
    document.close()
    with pytest.raises(EmptyDocumentError):
        PdfService().process(path, "image-only", path.name, path.stat().st_size, 100)