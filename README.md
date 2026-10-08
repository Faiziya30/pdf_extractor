# SmartPDF

SmartPDF is a document-processing foundation that extracts PDF metadata, page text, and a layout-based document outline. Day 1 focuses on reliable extraction and a clear review workflow; it does not include AI or RAG features.

## Current Features

- Safe PDF upload with extension, MIME, size, page-count, and content validation
- PyMuPDF metadata and page text extraction
- Heuristic heading detection using typography, numbering, casing, length, and spacing
- Clickable outline and page-wise results dashboard
- Consistent JSON errors and restricted local-development CORS
- Deterministic backend tests using generated PDF fixtures

## Architecture

The backend uses MVC-style boundaries: routes define HTTP paths, controllers manage request and document lifecycle, services contain PDF processing, schemas define API contracts, and models represent stored document records. Uploaded files are kept temporarily under `backend/uploads`; document records are held in memory for this phase.

## Tech Stack

- Backend: Python, FastAPI, Uvicorn, Pydantic, PyMuPDF
- Frontend: React, Vite, Tailwind CSS, Axios
- Tests: pytest, FastAPI TestClient

## Project Structure

```text
backend/
  app/
    config/        settings
    controllers/   HTTP-level document lifecycle
    exceptions/    predictable document errors
    models/        document records
    routes/        API route definitions
    schemas/       Pydantic response contracts
    services/      PyMuPDF extraction and heuristics
    utils/         file and response helpers
    main.py
  tests/
  requirements.txt
  .env.example
frontend/
  src/
    components/
    pages/
    services/
  package.json
  vite.config.js
```

## API Endpoints

- `GET /api/health`
- `POST /api/documents/upload` with multipart field `file`
- `GET /api/documents/{document_id}`
- `GET /api/documents/{document_id}/pages`
- `GET /api/documents/{document_id}/outline`
- `DELETE /api/documents/{document_id}`

## Setup

### Backend

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The Vite app runs at `http://localhost:5173`.

## Environment Variables

Copy `backend/.env.example` to `backend/.env` when needed. Set these variables in the shell or process manager:

- `MAX_FILE_SIZE_MB=50`
- `MAX_PAGES=100`
- `UPLOAD_DIR=uploads`
- `OUTPUT_DIR=outputs`
- `FRONTEND_URL=http://localhost:5173`

## Testing

```powershell
cd backend
venv\Scripts\Activate.ps1
pytest
```

## Current Limitations

Document records are held in memory and disappear when the backend restarts. Heading detection is an explainable layout heuristic, not AI. OCR, table and figure extraction, summaries, embeddings, RAG, authentication, accounts, and persistent storage are planned future phases and are not part of Day 1.
