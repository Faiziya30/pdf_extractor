import logging
import re
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any, Dict, List

import fitz

from app.exceptions.document_exceptions import EmptyDocumentError, InvalidDocumentError

logger = logging.getLogger(__name__)
NUMBERING_PATTERN = re.compile(r"^(?:\d+(?:\.\d+)*|[A-Z]|[IVXLCDM]+)[.)]?\s+", re.IGNORECASE)


class PdfService:
    """Extract page text and a layout-based document outline using PyMuPDF."""

    def process(self, path: Path, document_id: str, filename: str, file_size: int, max_pages: int) -> Dict[str, Any]:
        try:
            doc = fitz.open(path)
        except Exception as exc:
            logger.exception("Unable to open document %s", document_id)
            raise InvalidDocumentError() from exc

        try:
            if doc.page_count == 0:
                raise EmptyDocumentError()
            if doc.page_count > max_pages:
                raise InvalidDocumentError(f"The PDF exceeds the {max_pages}-page limit.")

            pages: List[Dict[str, Any]] = []
            blocks: List[Dict[str, Any]] = []
            for page_index, page in enumerate(doc):
                text = page.get_text("text").strip()
                pages.append({"page_number": page_index + 1, "text": text})
                blocks.extend(self._page_blocks(page, page_index + 1))

            if not any(page["text"] for page in pages):
                raise EmptyDocumentError()

            outline = self._build_outline(blocks)
            metadata = doc.metadata or {}
            return {
                "document": {
                    "id": document_id,
                    "filename": filename,
                    "page_count": doc.page_count,
                    "file_size": file_size,
                    "metadata": {
                        "title": metadata.get("title") or None,
                        "author": metadata.get("author") or None,
                        "subject": metadata.get("subject") or None,
                        "creator": metadata.get("creator") or None,
                        "producer": metadata.get("producer") or None,
                    },
                },
                "pages": pages,
                "outline": outline,
            }
        finally:
            doc.close()

    def _page_blocks(self, page: fitz.Page, page_number: int) -> List[Dict[str, Any]]:
        result = []
        raw_blocks = page.get_text("dict").get("blocks", [])
        for block_index, block in enumerate(raw_blocks):
            spans = [span for line in block.get("lines", []) for span in line.get("spans", [])]
            text = " ".join(span.get("text", "").strip() for span in spans).strip()
            if not text or not spans:
                continue
            primary = max(spans, key=lambda span: len(span.get("text", "")))
            result.append({
                "text": re.sub(r"\s+", " ", text),
                "page": page_number,
                "block_index": block_index,
                "font_size": float(primary.get("size", 0)),
                "font": primary.get("font", ""),
                "bold": bool(primary.get("flags", 0) & 16) or "bold" in primary.get("font", "").lower(),
                "top": float(block.get("bbox", [0, 0, 0, 0])[1]),
                "bottom": float(block.get("bbox", [0, 0, 0, 0])[3]),
            })
        return result

    def _build_outline(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not blocks:
            return []
        body_size = Counter(round(block["font_size"], 1) for block in blocks).most_common(1)[0][0]
        size_values = [block["font_size"] for block in blocks]
        largest_size = max(size_values)
        candidates = []
        previous_by_page: Dict[int, Dict[str, Any]] = {}
        for block in blocks:
            text = block["text"]
            word_count = len(text.split())
            if word_count > 18 or len(text) > 160 or self._looks_like_noise(text):
                previous_by_page[block["page"]] = block
                continue
            score = 0.0
            relative_size = block["font_size"] - body_size
            if relative_size >= 4:
                score += 0.34
            elif relative_size >= 2:
                score += 0.22
            elif relative_size >= 1:
                score += 0.10
            if block["font_size"] >= largest_size - 0.2:
                score += 0.10
            if block["bold"]:
                score += 0.20
            if NUMBERING_PATTERN.match(text):
                score += 0.22
            if text.isupper() and word_count <= 10:
                score += 0.12
            elif text.istitle() and word_count <= 10:
                score += 0.08
            if word_count <= 8:
                score += 0.08
            elif word_count > 12:
                score -= 0.10
            previous = previous_by_page.get(block["page"])
            if previous and block["top"] - previous["bottom"] > 10:
                score += 0.08
            if score >= 0.45 and (block["bold"] or relative_size >= 1 or NUMBERING_PATTERN.match(text)):
                candidates.append({"block": block, "score": min(score, 1.0)})
            previous_by_page[block["page"]] = block

        outline = []
        for candidate in candidates:
            block = candidate["block"]
            numbering = NUMBERING_PATTERN.match(block["text"])
            number_text = numbering.group(0).strip(" .)") if numbering else ""
            level = min(3, max(1, number_text.count(".") + 1)) if numbering else self._size_level(block["font_size"], body_size)
            outline.append({
                "text": block["text"],
                "level": level,
                "page": block["page"],
                "confidence": round(candidate["score"], 2),
            })
        return outline

    @staticmethod
    def _size_level(size: float, body_size: float) -> int:
        if size >= body_size + 4:
            return 1
        if size >= body_size + 2:
            return 2
        return 3

    @staticmethod
    def _looks_like_noise(text: str) -> bool:
        return bool(re.match(r"^(?:page\s+\d+|figure\s+\d+|table\s+\d+|https?://|copyright)", text, re.IGNORECASE))