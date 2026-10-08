import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fitz

from app.exceptions.document_exceptions import EmptyDocumentError, InvalidDocumentError

logger = logging.getLogger(__name__)
NUMBERING_PATTERN = re.compile(
    r"^(?P<number>(?:\d+(?:\.\d+)*[.)]?|[A-Z][.)]|[IVXLCDM]+(?:\.\d+)*[.)]?))\s+",
    re.IGNORECASE,
)
KNOWN_SHORT_HEADINGS = {"abstract", "conclusion", "references", "appendix", "summary"}


class PdfService:
    """Extract PDF content and an explainable layout-based document outline."""

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

            title, excluded_blocks = self._detect_document_title(blocks)
            outline = self._build_outline(blocks, excluded_blocks)
            metadata, metadata_status = self._extract_metadata(doc)
            return {
                "document": {
                    "id": document_id,
                    "filename": filename,
                    "title": title,
                    "page_count": doc.page_count,
                    "file_size": file_size,
                    "metadata": metadata,
                    "metadata_status": metadata_status,
                },
                "pages": pages,
                "outline": outline,
            }
        finally:
            doc.close()

    def _page_blocks(self, page: fitz.Page, page_number: int) -> List[Dict[str, Any]]:
        result = []
        page_width = page.rect.width
        page_height = page.rect.height
        raw_blocks = page.get_text("dict").get("blocks", [])
        for block_index, block in enumerate(raw_blocks):
            spans = [span for line in block.get("lines", []) for span in line.get("spans", [])]
            text = " ".join(span.get("text", "").strip() for span in spans).strip()
            if not text or not spans:
                continue
            bbox = block.get("bbox", [0, 0, 0, 0])
            primary = max(spans, key=lambda span: len(span.get("text", "")))
            result.append({
                "text": re.sub(r"\s+", " ", text),
                "page": page_number,
                "block_index": block_index,
                "font_size": float(primary.get("size", 0)),
                "font": primary.get("font", ""),
                "bold": bool(primary.get("flags", 0) & 16) or "bold" in primary.get("font", "").lower(),
                "italic": bool(primary.get("flags", 0) & 2) or "italic" in primary.get("font", "").lower(),
                "top": float(bbox[1]),
                "bottom": float(bbox[3]),
                "left": float(bbox[0]),
                "right": float(bbox[2]),
                "page_width": page_width,
                "page_height": page_height,
            })
        return result

    def _detect_document_title(self, blocks: List[Dict[str, Any]]) -> Tuple[Optional[str], set]:
        first_page = [block for block in blocks if block["page"] == 1]
        if not first_page:
            return None, set()
        body_size = self._body_size(blocks)
        candidates = []
        for block in first_page:
            text = block["text"]
            words = len(text.split())
            if block["top"] > block["page_height"] * 0.38 or words == 0 or words > 14:
                continue
            if NUMBERING_PATTERN.match(text) or (self._is_table_like(text) and block["font_size"] < body_size + 4):
                continue
            score = 0.0
            if block["font_size"] >= body_size + 4:
                score += 0.45
            elif block["font_size"] >= body_size + 2:
                score += 0.28
            if block["bold"]:
                score += 0.22
            if self._is_centered(block):
                score += 0.18
            if words <= 8:
                score += 0.10
            if block["top"] <= block["page_height"] * 0.22:
                score += 0.08
            candidates.append((score, block))
        if not candidates:
            return None, set()
        score, title_block = max(candidates, key=lambda item: item[0])
        if score < 0.45:
            return None, set()

        excluded = {title_block["block_index"]}
        for block in first_page:
            if block is title_block:
                continue
            close_to_title = 0 < block["top"] - title_block["bottom"] <= 90
            is_subtitle = close_to_title and len(block["text"].split()) <= 18 and not NUMBERING_PATTERN.match(block["text"])
            if is_subtitle and block["font_size"] <= title_block["font_size"]:
                excluded.add(block["block_index"])
        return title_block["text"], excluded

    def _build_outline(self, blocks: List[Dict[str, Any]], excluded_blocks: set) -> List[Dict[str, Any]]:
        if not blocks:
            return []
        body_size = self._body_size(blocks)
        largest_size = max(block["font_size"] for block in blocks)
        candidates = []
        previous_by_page: Dict[int, Dict[str, Any]] = {}
        for block in blocks:
            text = block["text"]
            words = len(text.split())
            numbering = NUMBERING_PATTERN.match(text)
            if block["block_index"] in excluded_blocks or words > 18 or len(text) > 160:
                previous_by_page[block["page"]] = block
                continue
            if self._looks_like_noise(text) or self._is_table_like(text):
                previous_by_page[block["page"]] = block
                continue

            relative_size = block["font_size"] - body_size
            score = 0.0
            if relative_size >= 4:
                score += 0.30
            elif relative_size >= 2:
                score += 0.18
            elif relative_size >= 1:
                score += 0.08
            if block["font_size"] >= largest_size - 0.2:
                score += 0.08
            if block["bold"]:
                score += 0.20
            if numbering:
                score += 0.30
            if text.isupper() and words <= 10:
                score += 0.10
            elif text.istitle() and words <= 10:
                score += 0.06
            if words <= 8:
                score += 0.06
            elif words > 12:
                score -= 0.10
            if text.rstrip().endswith(".") and not numbering:
                score -= 0.12
            previous = previous_by_page.get(block["page"])
            if previous and block["top"] - previous["bottom"] > 10:
                score += 0.08

            strong_context = bool(numbering) or block["bold"] or relative_size >= 2
            short_label = words <= 1
            if short_label and text.lower() not in KNOWN_SHORT_HEADINGS:
                strong_context = bool(numbering) or (block["bold"] and relative_size >= 4 and previous and block["top"] - previous["bottom"] > 16)
            if score >= 0.45 and strong_context:
                candidates.append({"block": block, "score": min(score, 1.0)})
            previous_by_page[block["page"]] = block

        outline = []
        for candidate in candidates:
            block = candidate["block"]
            numbering = NUMBERING_PATTERN.match(block["text"])
            level = self._numbering_level(numbering) if numbering else self._size_level(block["font_size"], body_size)
            outline.append({
                "text": block["text"],
                "level": level,
                "page": block["page"],
                "confidence": round(candidate["score"], 2),
            })
        return outline

    @staticmethod
    def _body_size(blocks: List[Dict[str, Any]]) -> float:
        return Counter(round(block["font_size"], 1) for block in blocks).most_common(1)[0][0]

    @staticmethod
    def _numbering_level(numbering: Optional[re.Match]) -> int:
        if not numbering:
            return 1
        value = numbering.group("number").rstrip(".)")
        return min(3, max(1, value.count(".") + 1))

    @staticmethod
    def _size_level(size: float, body_size: float) -> int:
        if size >= body_size + 4:
            return 1
        if size >= body_size + 2:
            return 2
        return 3

    @staticmethod
    def _is_centered(block: Dict[str, Any]) -> bool:
        center = (block["left"] + block["right"]) / 2
        return abs(center - block["page_width"] / 2) <= block["page_width"] * 0.18

    @staticmethod
    def _is_table_like(text: str) -> bool:
        numeric_tokens = re.findall(r"(?:\d+(?:[.,]\d+)*%?|[$€£]\s*\d+(?:[.,]\d+)*)", text)
        words = re.findall(r"[A-Za-z]+", text)
        if NUMBERING_PATTERN.match(text) and len(numeric_tokens) == 1:
            return False
        if re.search(r"\d+(?:\.\d+)?%", text) or re.search(r"[$€£]\s*\d", text):
            return True
        if len(numeric_tokens) >= 2:
            return True
        return len(words) <= 5 and len(numeric_tokens) >= 1 and any(char.isdigit() for char in text)

    @staticmethod
    def _looks_like_noise(text: str) -> bool:
        return bool(re.match(r"^(?:page\s+\d+|figure\s+\d+|table\s+\d+|https?://|copyright)", text, re.IGNORECASE))

    @staticmethod
    def _clean_metadata_value(value: Any) -> Optional[str]:
        if value is None:
            return None
        cleaned = str(value).strip()
        return cleaned or None

    def _extract_metadata(self, doc: fitz.Document) -> Tuple[Dict[str, Optional[str]], str]:
        try:
            raw = doc.metadata or {}
        except Exception:
            logger.exception("PDF metadata extraction failed")
            return {
                "title": None,
                "author": None,
                "subject": None,
                "creator": None,
                "producer": None,
                "creationDate": None,
                "modDate": None,
            }, "failed"
        metadata = {
            "title": self._clean_metadata_value(raw.get("title")),
            "author": self._clean_metadata_value(raw.get("author")),
            "subject": self._clean_metadata_value(raw.get("subject")),
            "creator": self._clean_metadata_value(raw.get("creator")),
            "producer": self._clean_metadata_value(raw.get("producer")),
            "creationDate": self._clean_metadata_value(raw.get("creationDate")),
            "modDate": self._clean_metadata_value(raw.get("modDate")),
        }
        return metadata, "available" if any(metadata.values()) else "empty"
