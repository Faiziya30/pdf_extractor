import fitz  # PyMuPDF
import json
import re
import os
from collections import defaultdict, Counter
from typing import Dict, List, Optional
import unicodedata
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

class PDFHeadingExtractor:
    def __init__(self):
        self.font_size_threshold = {
            'H1': 12,
            'H2': 11,
            'H3': 10,
            'H4': 9
        }
        
        self.heading_patterns = [
            r'^(Chapter|Section|Part|Appendix|Article)\s+\d+',  # Chapter 1, Article 1
            r'^\d+\.\s+',  # 1. Introduction
            r'^\d+\.\d+\s+',  # 1.1 Overview
            r'^\d+\.\d+\.\d+\s+',  # 1.1.1 Details
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS
            r'^[A-Z][a-z]+(\s+[A-Z][a-z]+)*$',  # Title Case
            r'^[IVXLCDM]+\.\s+',  # Roman numerals
            r'^[A-Z]\.\s+',  # A. B. C.
            r'^(Abstract|Introduction|Methodology|Results|Discussion|Conclusion|References|Summary|Background|Overview|Analysis|Recommendations|Appendix|Preface|Foreword)$',  # Common headings
            r'^第\d+章|^第\d+節',  # Japanese chapter/section
            r'^\d+\s+[A-Za-z]+$',  # e.g., "1 Introduction"
            r'^Part\s+[A-Z]$',  # Part A
        ]
        
        self.heading_keywords = {
            'en': ['summary', 'introduction', 'methodology', 'results', 'discussion', 'conclusion',
                   'background', 'analysis', 'approach', 'findings', 'recommendations', 'abstract',
                   'overview', 'objectives', 'scope', 'implementation', 'evaluation', 'appendix',
                   'preface', 'executive', 'strategy', 'performance'],
            'ja': ['序論', '結論', '要約', '概要', '背景', '方法', '結果', '考察', '参考文献'],
            'academic': ['literature review', 'related work', 'experimental setup', 'dataset',
                        'performance', 'benchmarks', 'comparative analysis', 'validation'],
            'business': ['executive summary', 'strategy', 'performance', 'analysis', 'recommendations'],
            'technical': ['architecture', 'design', 'implementation', 'testing', 'deployment']
        }
        
        self.persona_keywords = {
            'phd researcher': {
                'high': ['methodology', 'dataset', 'benchmark', 'performance', 'algorithm', 
                         'evaluation', 'experimental', 'validation', 'comparative', 'analysis',
                         'research', 'study', 'literature', 'hypothesis'],
                'medium': ['approach', 'framework', 'model', 'technique', 'method', 'results',
                          'findings', 'discussion', 'related work', 'references'],
                'low': ['introduction', 'background', 'overview', 'summary', 'conclusion']
            },
            'investment analyst': {
                'high': ['revenue', 'financial', 'market', 'investment', 'roi', 'growth',
                         'profitability', 'cash flow', 'valuation', 'risk', 'forecast'],
                'medium': ['strategy', 'performance', 'trends', 'analysis', 'competition',
                          'industry', 'outlook', 'metrics'],
                'low': ['overview', 'summary', 'background', 'introduction']
            },
            'undergraduate student': {
                'high': ['concept', 'definition', 'principle', 'theory', 'mechanism',
                         'example', 'application', 'practice', 'exercise', 'tutorial'],
                'medium': ['overview', 'introduction', 'summary', 'explanation',
                          'illustration', 'demonstration'],
                'low': ['advanced', 'research', 'detailed analysis', 'methodology']
            },
            'travel planner': {
                'high': ['itinerary', 'destination', 'activities', 'accommodation', 'sightseeing',
                         'group travel', 'tour', 'excursion', 'schedule', 'attractions'],
                'medium': ['plan', 'route', 'budget', 'logistics', 'recommendations', 'travel tips'],
                'low': ['introduction', 'overview', 'summary', 'background']
            }
        }
        
        self.exclude_patterns = [
            r'^\d+\s*[A-Z\s]+$',  # e.g., "3735 PARKWAY"
            r'^[A-Z]+:.*$',  # e.g., "ADDRESS:", "RSVP:"
            r'^(www\.|http).*$',  # URLs
            r'^\d+$',  # Numbers only
            r'^[-=]+$|^[-=]\s*[-=]+$',  # Lines of dashes or equals
            r'^\w+\s+\w+,\s+[A-Z]{2}\s+\d+$',  # Addresses
            r'^\(.*\)$',  # Parenthesized text
            r'^Page\s+\d+',  # Page numbers
            r'^Figure\s+\d+',  # Figure captions
            r'^Table\s+\d+',  # Table captions
            r'^\d{4}-\d{4}$',  # Year ranges
            r'^Copyright.*$',  # Copyright notices
            r'^\d+\.\d+\.\d+\.\d+\.\d+\.\d+\.\d+\.\d+$',  # Long numerical sequences
            r'^[0-9]{8,}$',  # Long number strings
            r'^\s*[-•]\s*.*$',  # List items
            r'^(Header|Footer)\s*\d*$',  # Header/Footer
            r'^(.)\1{3,}$',  # Repeated characters
        ]

    def clean_text(self, text: str) -> str:
        """Clean and normalize text, handling OCR noise"""
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)\[\]\"\'\/]', '', text)
        text = re.sub(r'(.)\1{3,}', r'\1', text)
        # Remove headers/footers and repetitive lines
        lines = text.split('\n')
        cleaned_lines = []
        prev_line = None
        count = 0
        for line in lines:
            line = line.strip()
            if line == prev_line:
                count += 1
                if count > 1:
                    continue
            else:
                count = 1
                prev_line = line
            if not re.match(r'^(Page\s+\d+|Header|Footer|Copyright.*)$', line, re.IGNORECASE):
                cleaned_lines.append(line)
        return ' '.join(cleaned_lines).strip()

    def is_excluded_text(self, text: str) -> bool:
        """Check if text should be excluded"""
        if not text or len(text.strip()) < 2:
            return True
        for pattern in self.exclude_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                logger.debug(f"Excluded by pattern: '{text}'")
                return True
        word_count = len(text.split())
        number_count = len(re.findall(r'\d+', text))
        if word_count > 0 and number_count / word_count > 0.6:
            return True
        if word_count > 30:
            return True
        return False

    def detect_language(self, text: str) -> str:
        """Detect language based on character scripts"""
        scripts = defaultdict(int)
        for char in text:
            script = unicodedata.name(char, '').split()[0] if unicodedata.name(char, '') else 'UNKNOWN'
            scripts[script] += 1
        if scripts.get('CJK', 0) > len(text) * 0.3:
            return 'ja'
        elif scripts.get('CYRILLIC', 0) > len(text) * 0.3:
            return 'ru'
        return 'en'

    def is_potential_heading(self, element: Dict) -> bool:
        """Check if element could be a heading"""
        text = element['text']
        font_info = element.get('font_info', {})
        if self.is_excluded_text(text):
            return False
        lang = self.detect_language(text)
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        if (element.get('is_bold', False) or 
            font_info.get('size', 10) >= 9.5 or
            text.isupper() or 
            text.istitle()):
            return True
        text_lower = text.lower()
        keywords = self.heading_keywords.get(lang, self.heading_keywords['en'])
        for keyword in keywords:
            if keyword in text_lower:
                return True
        return False

    def analyze_font_distribution(self, text_elements: List[Dict]) -> Dict:
        """Analyze font distribution for heading detection"""
        font_sizes = [elem['font_info']['size'] for elem in text_elements 
                      if 'font_info' in elem and 'size' in elem['font_info']]
        if not font_sizes:
            return {
                'body_size': 10,
                'h4_threshold': 9,
                'h3_threshold': 10,
                'h2_threshold': 11,
                'h1_threshold': 12
            }
        font_counter = Counter([round(size, 1) for size in font_sizes])
        sorted_sizes = sorted(font_counter.items(), key=lambda x: x[1], reverse=True)
        body_size = sorted_sizes[0][0] if sorted_sizes else 10
        size_diffs = sorted(set([round(size, 1) for size in font_sizes]), reverse=True)
        return {
            'body_size': body_size,
            'h4_threshold': size_diffs[3] if len(size_diffs) > 3 else max(9, body_size - 1),
            'h3_threshold': size_diffs[2] if len(size_diffs) > 2 else max(10, body_size - 0.5),
            'h2_threshold': size_diffs[1] if len(size_diffs) > 1 else max(11, body_size),
            'h1_threshold': size_diffs[0] if size_diffs else max(12, body_size + 0.5)
        }

    def calculate_heading_score(self, element: Dict, font_analysis: Dict, 
                              prev_element: Optional[Dict] = None, 
                              next_element: Optional[Dict] = None) -> float:
        """Calculate heading score with generic structural cues"""
        score = 0.0
        text = element.get('text', '')
        font_info = element.get('font_info', {})
        font_size = font_info.get('size', 10)
        
        if self.is_excluded_text(text):
            return 0.0
        
        # Font size scoring
        if font_size >= font_analysis['h1_threshold']:
            score += 40
        elif font_size >= font_analysis['h2_threshold']:
            score += 35
        elif font_size >= font_analysis['h3_threshold']:
            score += 30
        elif font_size >= font_analysis['h4_threshold']:
            score += 25
        
        # Formatting scoring
        if element.get('is_bold', False):
            score += 45
        if element.get('is_italic', False):
            score += 15
        
        # Pattern matching
        lang = self.detect_language(text)
        for pattern in self.heading_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                score += 50
                break
        
        # Keyword matching (generic)
        text_lower = text.lower()
        keywords = self.heading_keywords.get(lang, self.heading_keywords['en'])
        for keyword in keywords:
            if keyword in text_lower:
                score += 20
                break
        
        # Length scoring
        word_count = len(text.split())
        if word_count <= 7:
            score += 50
        elif word_count <= 12:
            score += 35
        elif word_count <= 20:
            score += 20
        else:
            score -= (word_count - 20) * 0.3
        
        # Case and structure
        if text.isupper():
            score += 25
        elif text.istitle():
            score += 20
        if re.match(r'^\d+\.', text) or re.match(r'^[A-Z]\.', text) or re.match(r'^[IVXLCDM]+\.', text):
            score += 25
        
        # Spatial analysis
        if prev_element and next_element:
            prev_bbox = prev_element.get('bbox', [0, 0, 0, 0])
            curr_bbox = element.get('bbox', [0, 0, 0, 0])
            next_bbox = next_element.get('bbox', [0, 0, 0, 0])
            space_before = curr_bbox[1] - prev_bbox[3] if prev_bbox[3] < curr_bbox[1] else 0
            space_after = next_bbox[1] - curr_bbox[3] if curr_bbox[3] < next_bbox[1] else 0
            if space_before > 1.0 or space_after > 1.0:
                score += 30
        
        logger.debug(f"Heading: {text}, Score: {score}, Font Size: {font_size}, Bold: {element.get('is_bold', False)}")
        return score

    def determine_heading_level(self, score: float, font_size: float, font_analysis: Dict) -> Optional[str]:
        """Determine heading level with relaxed thresholds"""
        if score < 40:
            logger.debug(f"Excluded as heading: Score: {score}, Font size: {font_size}")
            return None
        if font_size >= font_analysis['h1_threshold'] or score >= 85:
            return 'H1'
        elif font_size >= font_analysis['h2_threshold'] or score >= 70:
            return 'H2'
        elif font_size >= font_analysis['h3_threshold'] or score >= 55:
            return 'H3'
        elif score >= 40:
            return 'H4'
        logger.debug(f"Excluded as heading: Score: {score}, Font size: {font_size}")
        return None

    def extract_title(self, text_elements: List[Dict], pdf_path: str) -> str:
        """Extract document title using generic heuristics"""
        if not text_elements:
            return ""
        
        title_candidates = []
        max_font_size = max([e['font_info'].get('size', 0) for e in text_elements 
                            if 'font_info' in e] or [10])
        
        for i, element in enumerate(text_elements[:8]):  # Limit to first 8 elements
            if element['page'] == 0:  # Focus on page 1
                text = element['heading'] if 'heading' in element else element['text']
                font_info = element.get('font_info', {})
                if self.is_excluded_text(text):
                    continue
                title_score = 0
                font_size = font_info.get('size', 10)
                if font_size >= max_font_size:
                    title_score += 60
                elif font_size >= max_font_size - 0.5:
                    title_score += 50
                elif font_size >= max_font_size - 1:
                    title_score += 40
                title_score += max(0, 40 - i * 5)  # Prefer early elements
                word_count = len(text.split())
                if 3 <= word_count <= 20:
                    title_score += 40
                elif word_count <= 2:
                    title_score -= 25
                elif word_count > 30:
                    title_score -= 20
                if element.get('is_bold', False):
                    title_score += 35
                if element.get('is_italic', False):
                    title_score += 15
                # Spatial analysis
                if i > 0 and i < len(text_elements) - 1:
                    prev_bbox = text_elements[i-1].get('bbox', [0, 0, 0, 0])
                    curr_bbox = element.get('bbox', [0, 0, 0, 0])
                    next_bbox = text_elements[i+1].get('bbox', [0, 0, 0, 0])
                    space_before = curr_bbox[1] - prev_bbox[3] if prev_bbox[3] < curr_bbox[1] else 0
                    space_after = next_bbox[1] - curr_bbox[3] if curr_bbox[3] < next_bbox[1] else 0
                    if space_before > 1.5 or space_after > 1.5:
                        title_score += 25
                title_candidates.append({
                    'text': text,
                    'score': title_score,
                    'position': i,
                    'font_size': font_size
                })
        
        if title_candidates:
            title_candidates.sort(key=lambda x: (-x['score'], x['position']))
            selected_title = title_candidates[0]['text']
            logger.info(f"Selected Title: {selected_title}, Score: {title_candidates[0]['score']}, Font Size: {title_candidates[0]['font_size']}, Position: {title_candidates[0]['position']}")
            return selected_title
        
        logger.warning(f"No title found for {pdf_path}, returning empty string")
        return ""

    def score_relevance(self, text: str, persona: str, job_to_be_done: str) -> float:
        """Score text relevance based on persona and job-to-be-done"""
        if not text:
            return 0.0
        try:
            text = text[:2000]
            stop_words = set(stopwords.words('english'))
            text_tokens = set(word.lower() for word in word_tokenize(text) 
                            if word.isalnum() and word.lower() not in stop_words)
            persona_tokens = set(word.lower() for word in word_tokenize(persona) 
                               if word.isalnum() and word.lower() not in stop_words)
            job_tokens = set(word.lower() for word in word_tokenize(job_to_be_done) 
                           if word.isalnum() and word.lower() not in stop_words)
            
            score = 0.0
            persona_overlap = len(text_tokens.intersection(persona_tokens))
            job_overlap = len(text_tokens.intersection(job_tokens))
            score += persona_overlap * 15.0
            score += job_overlap * 25.0
            
            persona_lower = persona.lower()
            text_lower = text.lower()
            if 'researcher' in persona_lower or 'phd' in persona_lower:
                keywords = self.persona_keywords.get('phd researcher', {})
                for weight_category, weight_value in [('high', 20), ('medium', 10), ('low', 5)]:
                    for keyword in keywords.get(weight_category, []):
                        if keyword in text_lower:
                            score += weight_value
            elif 'analyst' in persona_lower or 'investment' in persona_lower:
                keywords = self.persona_keywords.get('investment analyst', {})
                for weight_category, weight_value in [('high', 20), ('medium', 10), ('low', 5)]:
                    for keyword in keywords.get(weight_category, []):
                        if keyword in text_lower:
                            score += weight_value
            elif 'student' in persona_lower or 'undergraduate' in persona_lower:
                keywords = self.persona_keywords.get('undergraduate student', {})
                for weight_category, weight_value in [('high', 20), ('medium', 10), ('low', 5)]:
                    for keyword in keywords.get(weight_category, []):
                        if keyword in text_lower:
                            score += weight_value
            elif 'travel planner' in persona_lower:
                keywords = self.persona_keywords.get('travel planner', {})
                for weight_category, weight_value in [('high', 30), ('medium', 15), ('low', 5)]:
                    for keyword in keywords.get(weight_category, []):
                        if keyword in text_lower:
                            score += weight_value
            
            job_lower = job_to_be_done.lower()
            if 'literature review' in job_lower:
                review_keywords = ['methodology', 'approach', 'study', 'research', 'analysis', 'literature', 'references']
                for keyword in review_keywords:
                    if keyword in text_lower:
                        score += 20
            elif 'revenue' in job_lower or 'financial' in job_lower:
                financial_keywords = ['revenue', 'profit', 'income', 'financial', 'market', 'investment', 'forecast']
                for keyword in financial_keywords:
                    if keyword in text_lower:
                        score += 20
            elif 'exam' in job_lower or 'study' in job_lower:
                study_keywords = ['concept', 'principle', 'definition', 'example', 'theory', 'tutorial']
                for keyword in study_keywords:
                    if keyword in text_lower:
                        score += 20
            elif 'trip' in job_lower or 'travel' in job_lower:
                travel_keywords = ['itinerary', 'destination', 'schedule', 'accommodation', 'activities']
                for keyword in travel_keywords:
                    if keyword in text_lower:
                        score += 25
            logger.debug(f"Relevance Score for text '{text[:50]}...': {score}")
            return max(0.0, score)
        except Exception as e:
            logger.error(f"Error in relevance scoring: {str(e)}")
            return 0.0

    def extract_text_with_formatting(self, doc: fitz.Document) -> List[Dict]:
        """Extract text with formatting, handling complex layouts"""
        text_elements = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            current_section = {
                'heading': '',
                'level': None,
                'page': page_num,
                'subsection_text': [],
                'font_info': {},
                'element': None
            }
            
            block_texts = []
            for block in blocks:
                if "lines" not in block:
                    continue
                block_text = ""
                font_info = {}
                
                for line in block["lines"]:
                    line_text = ""
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            cleaned_text = self.clean_text(text)
                            if cleaned_text:
                                line_text += cleaned_text + " "
                                font_info = {
                                    'font': span["font"],
                                    'size': span["size"],
                                    'flags': span["flags"],
                                    'color': span["color"],
                                    'bbox': span["bbox"]
                                }
                    if line_text.strip():
                        block_text += line_text.strip() + " "
                
                if block_text.strip():
                    block_texts.append({
                        'text': block_text.strip(),
                        'font_info': font_info,
                        'bbox': block.get('bbox', [0, 0, 0, 0]),
                        'is_bold': bool(font_info.get('flags', 0) & 2**4),
                        'is_italic': bool(font_info.get('flags', 0) & 2**1)
                    })
            
            # Merge nearby blocks
            merged_blocks = []
            i = 0
            while i < len(block_texts):
                current = block_texts[i]
                if i + 1 < len(block_texts):
                    next_block = block_texts[i + 1]
                    curr_bbox = current['bbox']
                    next_bbox = next_block['bbox']
                    if (abs(curr_bbox[1] - next_bbox[1]) < 6 and
                        abs(curr_bbox[0] - next_bbox[0]) < 50 and
                        abs(current['font_info'].get('size', 10) - next_block['font_info'].get('size', 10)) < 0.5):
                        current['text'] += " " + next_block['text']
                        current['bbox'] = [
                            min(curr_bbox[0], next_bbox[0]),
                            min(curr_bbox[1], next_bbox[1]),
                            max(curr_bbox[2], next_bbox[2]),
                            max(curr_bbox[3], next_bbox[3])
                        ]
                        i += 2
                        continue
                merged_blocks.append(current)
                i += 1
            
            for i, block in enumerate(merged_blocks):
                element = {
                    'text': block['text'],
                    'page': page_num,
                    'font_info': block['font_info'],
                    'bbox': block['bbox'],
                    'is_bold': block['is_bold'],
                    'is_italic': block['is_italic']
                }
                
                if self.is_potential_heading(element):
                    if current_section['heading']:
                        current_section['subsection_text'] = [p for p in current_section['subsection_text'] if p]
                        if current_section['subsection_text'] or current_section['heading']:
                            text_elements.append(current_section.copy())
                    current_section = {
                        'heading': element['text'],
                        'level': None,
                        'page': page_num,
                        'subsection_text': [],
                        'font_info': element['font_info'],
                        'element': element
                    }
                else:
                    current_section['subsection_text'].append(element['text'])
                
            if current_section['heading']:
                current_section['subsection_text'] = [p for p in current_section['subsection_text'] if p]
                if current_section['subsection_text'] or current_section['heading']:
                    text_elements.append(current_section.copy())
        
        logger.info(f"Extracted {len(text_elements)} text elements")
        for elem in text_elements[:10]:
            logger.debug(f"Element: {elem['heading']}, Page: {elem['page']}, Font Size: {elem['font_info'].get('size', 10)}")
        return text_elements

    def process_pdf(self, pdf_path: str, font_analysis: Optional[Dict] = None, 
                   for_round_1b: bool = False, persona: str = "", job_to_be_done: str = "") -> Dict:
        """Process a single PDF for Round 1A or 1B"""
        try:
            doc = fitz.open(pdf_path)
            if doc.page_count > 50:
                doc.close()
                logger.warning(f"PDF {pdf_path} exceeds 50 pages, skipping")
                return {
                    "title": "",
                    "outline": [],
                    "text_elements": [] if for_round_1b else None,
                    "font_analysis": font_analysis,
                    "document": os.path.basename(pdf_path) if for_round_1b else None
                }
            
            logger.info(f"Processing PDF: {pdf_path}, Pages: {doc.page_count}")
            text_elements = self.extract_text_with_formatting(doc)
            
            if not text_elements:
                doc.close()
                logger.warning(f"No text elements extracted from {pdf_path}")
                return {
                    "title": "",
                    "outline": [],
                    "text_elements": [] if for_round_1b else None,
                    "font_analysis": font_analysis,
                    "document": os.path.basename(pdf_path) if for_round_1b else None
                }
            
            all_elements = []
            for elem in text_elements:
                if 'element' in elem:
                    all_elements.append(elem['element'])
            
            font_analysis = font_analysis or self.analyze_font_distribution(all_elements)
            logger.debug(f"Font Analysis: {font_analysis}")
            title = self.extract_title(text_elements, pdf_path)
            
            processed_elements = []
            for i, elem in enumerate(text_elements):
                if 'element' in elem:
                    prev_elem = text_elements[i - 1]['element'] if i > 0 else None
                    next_elem = text_elements[i + 1]['element'] if i < len(text_elements) - 1 else None
                    score = self.calculate_heading_score(elem['element'], font_analysis, prev_elem, next_elem)
                    level = self.determine_heading_level(score, elem['font_info'].get('size', 10), font_analysis)
                    if level:
                        processed_elements.append({
                            'heading': elem['heading'],
                            'level': level,
                            'page': elem['page'],
                            'subsection_text': elem['subsection_text'],
                            'score': score
                        })
            
            seen = set()
            unique_elements = []
            for elem in processed_elements:
                key = (elem['heading'], elem['page'])
                if key not in seen:
                    seen.add(key)
                    unique_elements.append(elem)
            
            unique_elements.sort(key=lambda x: (x['page'], -x['score']))
            
            outline = [{
                'level': elem['level'],
                'text': elem['heading'],
                'page': elem['page'] + 1
            } for elem in unique_elements]
            
            doc.close()
            
            result = {
                "title": title,
                "outline": outline
            }
            
            if for_round_1b:
                result.update({
                    "text_elements": unique_elements,
                    "font_analysis": font_analysis,
                    "document": os.path.basename(pdf_path)
                })
            
            logger.info(f"PDF {pdf_path} processed: Title='{title}', Headings={len(outline)}")
            return result
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            return {
                "title": "",
                "outline": [],
                "text_elements": [] if for_round_1b else None,
                "font_analysis": font_analysis,
                "document": os.path.basename(pdf_path) if for_round_1b else None
            }

    def process_pdf_collection(self, input_dir: str, documents: List[Dict], 
                              persona: str, job_to_be_done: str) -> List[Dict]:
        """Process multiple PDFs for Round 1B"""
        results = []
        font_analysis = None
        for doc in documents:
            doc_name = doc.get('filename', '') if isinstance(doc, dict) else doc
            if not doc_name:
                logger.warning(f"Invalid document entry: {doc}")
                continue
            pdf_path = os.path.join(input_dir, doc_name)
            if not os.path.exists(pdf_path):
                logger.warning(f"PDF {doc_name} not found in {input_dir}")
                continue
            result = self.process_pdf(pdf_path, font_analysis, True, persona, job_to_be_done)
            if not font_analysis:
                font_analysis = result.get('font_analysis')
            result.pop('font_analysis', None)
            results.append(result)
        return results

def main():
    """Main function for Round 1A and 1B execution"""
    input_dir = "input"
    output_dir = "output"
    input_json_path = os.path.join(input_dir, "input.json")
    
    os.makedirs(output_dir, exist_ok=True)
    extractor = PDFHeadingExtractor()
    
    # Round 1B: Check for input.json
    if os.path.exists(input_json_path):
        try:
            with open(input_json_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading input JSON: {str(e)}")
            return
        
        documents = input_data.get('documents', [])
        persona_dict = input_data.get('persona', {})
        job_dict = input_data.get('job_to_be_done', {})
        
        persona = persona_dict.get('role', '') if isinstance(persona_dict, dict) else persona_dict
        job_to_be_done = job_dict.get('task', '') if isinstance(job_dict, dict) else job_to_be_done
        
        logger.info(f"Processing {len(documents)} documents for persona: {persona}, job: {job_to_be_done}")
        
        pdf_results = extractor.process_pdf_collection(input_dir, documents, persona, job_to_be_done)
        
        extracted_sections = []
        subsection_analysis = []
        
        for pdf_result in pdf_results:
            doc_name = pdf_result['document']
            for heading in pdf_result['outline']:
                section_text = heading['text']
                relevance_score = extractor.score_relevance(section_text, persona, job_to_be_done)
                extracted_sections.append({
                    'document': doc_name,
                    'page_number': heading['page'],
                    'section_title': heading['text'],
                    'relevance_score': relevance_score
                })
            for element in pdf_result['text_elements']:
                if element['subsection_text']:
                    subsection_text = ' '.join(element['subsection_text'])
                    subsection_score = extractor.score_relevance(subsection_text, persona, job_to_be_done)
                    refined_text = subsection_text[:1000]
                    if len(subsection_text) > 1000:
                        refined_text += "..."
                    subsection_analysis.append({
                        'document': doc_name,
                        'refined_text': refined_text,
                        'page_number': element['page'] + 1,
                        'relevance_score': subsection_score
                    })
        
        extracted_sections.sort(key=lambda x: x['relevance_score'], reverse=True)
        for i, section in enumerate(extracted_sections):
            section['importance_rank'] = i + 1
            del section['relevance_score']
        
        subsection_analysis.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        output = {
            'metadata': {
                'input_documents': [doc.get('filename', doc) for doc in documents],
                'persona': persona,
                'job_to_be_done': job_to_be_done,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            },
            'extracted_sections': extracted_sections,
            'subsection_analysis': subsection_analysis
        }
        
        output_path = os.path.join(output_dir, 'output.json')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            logger.info(f"Output saved: {output_path}")
            logger.info(f"Summary: {len(pdf_results)} documents, {len(extracted_sections)} sections, {len(subsection_analysis)} subsections")
        except Exception as e:
            logger.error(f"Error writing output: {str(e)}")
    else:
        # Round 1A: Process individual PDFs
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(input_dir, filename)
                output_filename = os.path.splitext(filename)[0] + '.json'
                output_path = os.path.join(output_dir, output_filename)
                
                logger.info(f"Processing: {filename}")
                result = extractor.process_pdf(pdf_path)
                
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump({"title": result["title"], "outline": result["outline"]}, 
                                 f, ensure_ascii=False, indent=2)
                    logger.info(f"Output saved: {output_filename}")
                except Exception as e:
                    logger.error(f"Error writing output for {output_filename}: {str(e)}")

if __name__ == "__main__":
    main()
