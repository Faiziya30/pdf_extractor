#!/usr/bin/env python3
"""
PDF Outline Extractor for Adobe Hackathon Round 1A
Extracts title and hierarchical headings (H1, H2, H3) from PDFs
"""

import os
import json
import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        # Font size thresholds for heading detection
        self.font_size_thresholds = {
            'title': 20,
            'h1': 16,
            'h2': 14,
            'h3': 12
        }
        
        # Common heading patterns
        self.heading_patterns = [
            r'^\d+\.\s+',  # 1. Introduction
            r'^\d+\.\d+\s+',  # 1.1 Overview
            r'^\d+\.\d+\.\d+\s+',  # 1.1.1 Details
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^Chapter\s+\d+',  # Chapter 1
            r'^Section\s+\d+',  # Section 1
            r'^[IVX]+\.\s+',  # Roman numerals
        ]
    
    def extract_text_with_formatting(self, pdf_path: str) -> List[Dict]:
        """Extract text with font information from PDF"""
        doc = fitz.open(pdf_path)
        formatted_text = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            if text:
                                formatted_text.append({
                                    'text': text,
                                    'page': page_num + 1,
                                    'font_size': span["size"],
                                    'font_flags': span["flags"],
                                    'bbox': span["bbox"]
                                })
        
        doc.close()
        return formatted_text
    
    def is_bold(self, flags: int) -> bool:
        """Check if text is bold based on font flags"""
        return bool(flags & 2**4)
    
    def classify_heading_level(self, text: str, font_size: float, is_bold: bool, page: int) -> Optional[str]:
        """Classify text as title, H1, H2, H3, or None"""
        text = text.strip()
        
        # Skip very short text or page numbers
        if len(text) < 3 or text.isdigit():
            return None
        
        # Skip common non-heading patterns
        skip_patterns = [
            r'^\d+
    
    def extract_title(self, formatted_text: List[Dict]) -> str:
        """Extract document title"""
        title_candidates = []
        
        # Look for title in first 3 pages
        for item in formatted_text[:50]:  # Check first 50 text items
            if item['page'] <= 3:
                classification = self.classify_heading_level(
                    item['text'], 
                    item['font_size'], 
                    self.is_bold(item['font_flags']), 
                    item['page']
                )
                if classification == 'title':
                    title_candidates.append((item['text'], item['font_size']))
        
        if title_candidates:
            # Return the title with largest font size
            return max(title_candidates, key=lambda x: x[1])[0]
        
        # Fallback: use filename without extension
        return "Document"
    
    def extract_outline(self, formatted_text: List[Dict], title: str) -> List[Dict]:
        """Extract hierarchical outline"""
        outline = []
        seen_headings = set()
        
        for item in formatted_text:
            text = item['text']
            
            # Skip the title if we already found it
            if text.strip() == title.strip():
                continue
            
            classification = self.classify_heading_level(
                text, 
                item['font_size'], 
                self.is_bold(item['font_flags']), 
                item['page']
            )
            
            if classification in ['H1', 'H2', 'H3']:
                # Clean up the text
                clean_text = re.sub(r'^\d+\.\s*', '', text)  # Remove numbering
                clean_text = re.sub(r'^\d+\.\d+\s*', '', clean_text)
                clean_text = re.sub(r'^\d+\.\d+\.\d+\s*', '', clean_text)
                clean_text = clean_text.strip()
                
                # Avoid duplicates (case-insensitive)
                text_key = (clean_text.lower(), item['page'], classification)
                if text_key not in seen_headings and len(clean_text) > 2:
                    outline.append({
                        'level': classification,
                        'text': clean_text,
                        'page': item['page']
                    })
                    seen_headings.add(text_key)
        
        # Sort by page number and maintain hierarchy
        outline.sort(key=lambda x: (x['page'], x['level']))
        
        return outline
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a single PDF and extract outline"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract formatted text
            formatted_text = self.extract_text_with_formatting(pdf_path)
            
            if not formatted_text:
                logger.warning(f"No text extracted from {pdf_path}")
                return {
                    "title": Path(pdf_path).stem,
                    "outline": []
                }
            
            # Extract title and outline
            title = self.extract_title(formatted_text)
            outline = self.extract_outline(formatted_text, title)
            
            result = {
                "title": title,
                "outline": outline
            }
            
            logger.info(f"Extracted title: {title}")
            logger.info(f"Found {len(outline)} headings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": []
            }

def main():
    """Main execution function"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDFs in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    for pdf_file in pdf_files:
        try:
            # Extract outline
            result = extractor.process_pdf(str(pdf_file))
            
            # Save to output directory
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved output to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")

if __name__ == "__main__":
    main()
,  # Just numbers
            r'^page\s+\d+',  # Page numbers
            r'^figure\s+\d+',  # Figure captions
            r'^table\s+\d+',  # Table captions
            r'^\w+@\w+\.\w+',  # Email addresses
            r'^https?://',  # URLs
            r'^www\.',  # Web addresses
            r'^\d+\s*-\s*\d+
    
    def extract_title(self, formatted_text: List[Dict]) -> str:
        """Extract document title"""
        title_candidates = []
        
        # Look for title in first 3 pages
        for item in formatted_text[:50]:  # Check first 50 text items
            if item['page'] <= 3:
                classification = self.classify_heading_level(
                    item['text'], 
                    item['font_size'], 
                    self.is_bold(item['font_flags']), 
                    item['page']
                )
                if classification == 'title':
                    title_candidates.append((item['text'], item['font_size']))
        
        if title_candidates:
            # Return the title with largest font size
            return max(title_candidates, key=lambda x: x[1])[0]
        
        # Fallback: use filename without extension
        return "Document"
    
    def extract_outline(self, formatted_text: List[Dict], title: str) -> List[Dict]:
        """Extract hierarchical outline"""
        outline = []
        seen_headings = set()
        
        for item in formatted_text:
            text = item['text']
            
            # Skip the title if we already found it
            if text.strip() == title.strip():
                continue
            
            classification = self.classify_heading_level(
                text, 
                item['font_size'], 
                self.is_bold(item['font_flags']), 
                item['page']
            )
            
            if classification in ['H1', 'H2', 'H3']:
                # Clean up the text
                clean_text = re.sub(r'^\d+\.\s*', '', text)  # Remove numbering
                clean_text = re.sub(r'^\d+\.\d+\s*', '', clean_text)
                clean_text = re.sub(r'^\d+\.\d+\.\d+\s*', '', clean_text)
                clean_text = clean_text.strip()
                
                # Avoid duplicates (case-insensitive)
                text_key = (clean_text.lower(), item['page'], classification)
                if text_key not in seen_headings and len(clean_text) > 2:
                    outline.append({
                        'level': classification,
                        'text': clean_text,
                        'page': item['page']
                    })
                    seen_headings.add(text_key)
        
        # Sort by page number and maintain hierarchy
        outline.sort(key=lambda x: (x['page'], x['level']))
        
        return outline
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a single PDF and extract outline"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract formatted text
            formatted_text = self.extract_text_with_formatting(pdf_path)
            
            if not formatted_text:
                logger.warning(f"No text extracted from {pdf_path}")
                return {
                    "title": Path(pdf_path).stem,
                    "outline": []
                }
            
            # Extract title and outline
            title = self.extract_title(formatted_text)
            outline = self.extract_outline(formatted_text, title)
            
            result = {
                "title": title,
                "outline": outline
            }
            
            logger.info(f"Extracted title: {title}")
            logger.info(f"Found {len(outline)} headings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": []
            }

def main():
    """Main execution function"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDFs in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    for pdf_file in pdf_files:
        try:
            # Extract outline
            result = extractor.process_pdf(str(pdf_file))
            
            # Save to output directory
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved output to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")

if __name__ == "__main__":
    main()
,  # Page ranges like "1-5"
            r'^[^\w\s]{3,}
    
    def extract_title(self, formatted_text: List[Dict]) -> str:
        """Extract document title"""
        title_candidates = []
        
        # Look for title in first 3 pages
        for item in formatted_text[:50]:  # Check first 50 text items
            if item['page'] <= 3:
                classification = self.classify_heading_level(
                    item['text'], 
                    item['font_size'], 
                    self.is_bold(item['font_flags']), 
                    item['page']
                )
                if classification == 'title':
                    title_candidates.append((item['text'], item['font_size']))
        
        if title_candidates:
            # Return the title with largest font size
            return max(title_candidates, key=lambda x: x[1])[0]
        
        # Fallback: use filename without extension
        return "Document"
    
    def extract_outline(self, formatted_text: List[Dict], title: str) -> List[Dict]:
        """Extract hierarchical outline"""
        outline = []
        seen_headings = set()
        
        for item in formatted_text:
            text = item['text']
            
            # Skip the title if we already found it
            if text.strip() == title.strip():
                continue
            
            classification = self.classify_heading_level(
                text, 
                item['font_size'], 
                self.is_bold(item['font_flags']), 
                item['page']
            )
            
            if classification in ['H1', 'H2', 'H3']:
                # Clean up the text
                clean_text = re.sub(r'^\d+\.\s*', '', text)  # Remove numbering
                clean_text = re.sub(r'^\d+\.\d+\s*', '', clean_text)
                clean_text = re.sub(r'^\d+\.\d+\.\d+\s*', '', clean_text)
                clean_text = clean_text.strip()
                
                # Avoid duplicates (case-insensitive)
                text_key = (clean_text.lower(), item['page'], classification)
                if text_key not in seen_headings and len(clean_text) > 2:
                    outline.append({
                        'level': classification,
                        'text': clean_text,
                        'page': item['page']
                    })
                    seen_headings.add(text_key)
        
        # Sort by page number and maintain hierarchy
        outline.sort(key=lambda x: (x['page'], x['level']))
        
        return outline
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a single PDF and extract outline"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract formatted text
            formatted_text = self.extract_text_with_formatting(pdf_path)
            
            if not formatted_text:
                logger.warning(f"No text extracted from {pdf_path}")
                return {
                    "title": Path(pdf_path).stem,
                    "outline": []
                }
            
            # Extract title and outline
            title = self.extract_title(formatted_text)
            outline = self.extract_outline(formatted_text, title)
            
            result = {
                "title": title,
                "outline": outline
            }
            
            logger.info(f"Extracted title: {title}")
            logger.info(f"Found {len(outline)} headings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": []
            }

def main():
    """Main execution function"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDFs in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    for pdf_file in pdf_files:
        try:
            # Extract outline
            result = extractor.process_pdf(str(pdf_file))
            
            # Save to output directory
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved output to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")

if __name__ == "__main__":
    main()
,  # Only symbols
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, text.lower()):
                return None
        
        # Title detection (usually on first few pages with large font)
        if page <= 3 and font_size >= self.font_size_thresholds['title']:
            return 'title'
        
        # Heading detection based on patterns and formatting
        has_heading_pattern = any(re.match(pattern, text) for pattern in self.heading_patterns)
        is_all_caps = text.isupper() and len(text.split()) <= 8 and len(text) > 3
        
        # Enhanced heading detection with relative font size consideration
        # H1 detection - largest headings
        if (font_size >= self.font_size_thresholds['h1'] or 
            (is_bold and font_size >= 14 and has_heading_pattern) or 
            (is_all_caps and is_bold) or
            re.match(r'^\d+\.\s+[A-Z]', text)):  # "1. Introduction" pattern
            return 'H1'
        
        # H2 detection - medium headings
        elif (font_size >= self.font_size_thresholds['h2'] or 
              (is_bold and font_size >= 12 and has_heading_pattern) or
              re.match(r'^\d+\.\d+\s+[A-Z]', text)):  # "1.1 Overview" pattern
            return 'H2'
        
        # H3 detection - smaller headings
        elif (font_size >= self.font_size_thresholds['h3'] or 
              (is_bold and font_size >= 10 and has_heading_pattern) or
              re.match(r'^\d+\.\d+\.\d+\s+[A-Z]', text)):  # "1.1.1 Details" pattern
            return 'H3'
        
        return None
    
    def extract_title(self, formatted_text: List[Dict]) -> str:
        """Extract document title"""
        title_candidates = []
        
        # Look for title in first 3 pages
        for item in formatted_text[:50]:  # Check first 50 text items
            if item['page'] <= 3:
                classification = self.classify_heading_level(
                    item['text'], 
                    item['font_size'], 
                    self.is_bold(item['font_flags']), 
                    item['page']
                )
                if classification == 'title':
                    title_candidates.append((item['text'], item['font_size']))
        
        if title_candidates:
            # Return the title with largest font size
            return max(title_candidates, key=lambda x: x[1])[0]
        
        # Fallback: use filename without extension
        return "Document"
    
    def extract_outline(self, formatted_text: List[Dict], title: str) -> List[Dict]:
        """Extract hierarchical outline"""
        outline = []
        seen_headings = set()
        
        for item in formatted_text:
            text = item['text']
            
            # Skip the title if we already found it
            if text.strip() == title.strip():
                continue
            
            classification = self.classify_heading_level(
                text, 
                item['font_size'], 
                self.is_bold(item['font_flags']), 
                item['page']
            )
            
            if classification in ['H1', 'H2', 'H3']:
                # Clean up the text
                clean_text = re.sub(r'^\d+\.\s*', '', text)  # Remove numbering
                clean_text = re.sub(r'^\d+\.\d+\s*', '', clean_text)
                clean_text = re.sub(r'^\d+\.\d+\.\d+\s*', '', clean_text)
                clean_text = clean_text.strip()
                
                # Avoid duplicates (case-insensitive)
                text_key = (clean_text.lower(), item['page'], classification)
                if text_key not in seen_headings and len(clean_text) > 2:
                    outline.append({
                        'level': classification,
                        'text': clean_text,
                        'page': item['page']
                    })
                    seen_headings.add(text_key)
        
        # Sort by page number and maintain hierarchy
        outline.sort(key=lambda x: (x['page'], x['level']))
        
        return outline
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Process a single PDF and extract outline"""
        try:
            logger.info(f"Processing: {pdf_path}")
            
            # Extract formatted text
            formatted_text = self.extract_text_with_formatting(pdf_path)
            
            if not formatted_text:
                logger.warning(f"No text extracted from {pdf_path}")
                return {
                    "title": Path(pdf_path).stem,
                    "outline": []
                }
            
            # Extract title and outline
            title = self.extract_title(formatted_text)
            outline = self.extract_outline(formatted_text, title)
            
            result = {
                "title": title,
                "outline": outline
            }
            
            logger.info(f"Extracted title: {title}")
            logger.info(f"Found {len(outline)} headings")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": []
            }

def main():
    """Main execution function"""
    input_dir = Path("input")
    output_dir = Path("output")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(exist_ok=True)
    
    extractor = PDFOutlineExtractor()
    
    # Process all PDFs in input directory
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return
    
    for pdf_file in pdf_files:
        try:
            # Extract outline
            result = extractor.process_pdf(str(pdf_file))
            
            # Save to output directory
            output_file = output_dir / f"{pdf_file.stem}.json"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved output to: {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")

if __name__ == "__main__":
    main()