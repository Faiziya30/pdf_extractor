# Smart PDF Insight - Backend

This is the backend component for the Adobe India Hackathon "Connecting the Dots" challenge, providing PDF processing capabilities for both Round 1A (Outline Extraction) and Round 1B (Persona-driven Document Intelligence).

## 🏗️ Architecture

```
backend/
├── app/
│   ├── input/                 # Temporary PDF storage
│   ├── output/                # JSON output storage
│   ├── pdf_extractor.py       # Core PDF processing logic
│   └── test_validation.py     # Testing utilities
├── app.py                     # Flask API server
├── batch_process.py           # Standalone batch processor for Docker
├── requirements.txt           # Python dependencies
├── dockerfile                 # Container configuration
└── README.md                  # This file
```

## 🚀 Features

### Round 1A: Document Outline Extraction
- Extracts structured outlines (Title, H1, H2, H3) from PDFs
- Intelligent heading detection using multiple strategies:
  - Font size analysis
  - Pattern matching (numbered sections, keywords)
  - Bold text detection
  - Positional analysis
- Supports multilingual documents
- Fast processing (≤10 seconds for 50-page PDFs)

### Round 1B: Persona-driven Document Intelligence
- Analyzes multiple documents based on user persona and job requirements
- Extracts and ranks relevant sections
- Provides subsection analysis with refined text
- Keyword-based relevance scoring
- Supports diverse document types and personas

## 📋 Requirements

- Python 3.11+
- CPU-only processing (no GPU required)
- 8 CPUs, 16GB RAM recommended
- Model size ≤ 200MB (Round 1A) / ≤ 1GB (Round 1B)
- No internet access required (offline processing)

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create necessary directories:**
   ```bash
   mkdir -p app/input app/output
   ```

## 🎯 Usage

### Development Server

Start the Flask development server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 1. Health Check
```bash
GET /health
```

#### 2. Extract Outline (Round 1A)
```bash
POST /extract-outline
Content-Type: multipart/form-data
Body: file=<pdf_file>
```

#### 3. Analyze Documents (Round 1B)
```bash
POST /analyze-documents
Content-Type: multipart/form-data
Body: 
  files=<pdf_files>
  persona=<persona_description>
  job_to_be_done=<job_description>
```

#### 4. Batch Process (Docker)
```bash
POST /batch-process
```

### Testing

#### Round 1A Testing
```bash
python app/test_validation.py 1A sample.pdf [expected_output.json]
```

#### Round 1B Testing
```bash
python app/test_validation.py 1B doc1.pdf doc2.pdf --persona "Researcher" --job "Literature review"
```

### Docker Usage

For hackathon submission, the container will be run as:
```bash
docker build --platform linux/amd64 -t mysolutionname:identifier .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none mysolutionname:identifier
```

## 🧠 Core Algorithm

### Heading Detection Strategy

1. **Font Analysis**: Identifies headings based on font size percentiles
2. **Pattern Matching**: Recognizes numbered sections (1., 1.1., 1.1.1.)
3. **Keyword Detection**: Looks for common heading words (Introduction, Methods, etc.)
4. **Structural Analysis**: Uses document structure and positioning
5. **Bold Text Detection**: Considers font styling
6. **Header/Footer Filtering**: Removes page numbers and repetitive content

### Relevance Scoring Algorithm

For Round 1B, the system uses a multi-factor scoring approach:
- **Persona Keywords**: 0.3 weight per match
- **Job Keywords**: 0.5 weight per match
- **Multiple Matches Bonus**: Additional 0.2 for 3+ keyword matches
- **Content Length Factor**: Normalizes by content length
- **Section Ranking**: Importance ranking from 1-10

## 📊 Performance Metrics

### Round 1A Constraints
- ⏱️ Processing Time: ≤ 10 seconds per 50-page PDF
- 💾 Model Size: ≤ 200MB
- 🚫 Network: No internet access
- 🏗️ Architecture: AMD64 CPU only

### Round 1B Constraints
- ⏱️ Processing Time: ≤ 60 seconds for 3-5 documents
- 💾 Model Size: ≤ 1GB
- 🚫 Network: No internet access
- 🏗️ Architecture: AMD64 CPU only

## 🎨 Output Formats

### Round 1A Output
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Introduction",
      "page": 1
    }
  ]
}
```

### Round 1B Output
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf"],
    "persona": "Researcher",
    "job_to_be_done": "Literature review",
    "processing_timestamp": "2025-01-XX"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 1,
      "section_title": "Introduction",
      "importance_rank": 9
    }
  ],
  "sub_section_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 1,
      "refined_text": "Relevant subsection content..."
    }
  ]
}
```

## 🔧 Dependencies

- **Flask**: Web framework for API
- **PyMuPDF (fitz)**: PDF text extraction and analysis
- **PyPDF2**: Additional PDF processing
- **NumPy**: Numerical operations for scoring
- **Flask-CORS**: Cross-origin resource sharing

## 🐛 Troubleshooting

### Common Issues

1. **Font Analysis Issues**: The system uses multiple fallback strategies if font size detection fails
2. **Multilingual Support**: Regex patterns are designed to work with various languages
3. **Memory Usage**: Processing is optimized to handle large documents within memory constraints
4. **Docker Compatibility**: Dockerfile specifies AMD64 platform for compatibility

### Error Handling

- Graceful fallbacks for corrupted PDFs
- Error logging with detailed messages
- Partial results returned when possible
- Timeout protection for large documents

## 📈 Optimization Features

- **Efficient Text Extraction**: Uses PyMuPDF for fast PDF processing
- **Smart Caching**: Avoids redundant processing
- **Memory Management**: Processes documents in chunks
- **Parallel Processing**: Ready for multi-document analysis
- **Constraint Compliance**: All processing within specified limits

## 🏆 Hackathon Compliance

This backend implementation fully complies with all hackathon requirements:
- ✅ Round 1A: Extract structured outlines with proper JSON format
- ✅ Round 1B: Persona-driven document intelligence
- ✅ Docker compatibility with AMD64 architecture
- ✅ Offline processing (no network calls)
- ✅ Performance constraints met
- ✅ Proper error handling and logging
- ✅ Modular, extensible code structure

The solution is ready for integration with the frontend and Docker deployment for the hackathon submission.
