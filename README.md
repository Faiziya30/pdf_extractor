# Smart-PDF-Insight

Smart-PDF-Insight is a web application designed to extract structured outlines from PDF documents. It features a Flask-based backend for processing PDFs and a React frontend with Tailwind CSS for a user-friendly interface. Users can upload PDFs, preview them, and view extracted headings in an organized format, making it ideal for document analysis and summarization.

## Project Structure

```
Smart-PDF-Insight/
│
├── backend/                        # 🔙 Flask app
│   ├── app/
│   │   ├── input/                 # ⬆ Uploaded PDFs go here temporarily
│   │   ├── output/                # 📤 Stores JSON outputs (optional for batch processing)
│   │   ├── __pycache__/
│   │   ├── pdf_extractor.py       # 🧠 PDF extraction logic
│   │   └── test_validation.py     # ✅ Unit tests (optional)
│   ├── app.py                     # 🚀 Flask API entry point
│   ├── requirements.txt           # 📦 Python dependencies
│   ├── dockerfile                 # 🐳 Docker configuration (optional)
│   ├── docker-compose.yml         # 🐳 Local testing setup (optional)
│   └── .gitignore                 # ❌ Ignores venv, __pycache__, etc.
│
├── frontend/                      # 🎨 React App
│   ├── public/                    # Static assets
│   ├── src/
│   │   ├── assets/                # Images, fonts, etc.
│   │   ├── components/            # Reusable React components
│   │   ├── pages/
│   │   │   ├── Home.jsx           # 🏠 Home page
│   │   │   ├── Upload.jsx         # 📤 PDF upload and preview page
│   │   │   └── Results.jsx        # 📊 Results display page
│   │   ├── services/
│   │   │   └── api.js             # 🔌 Axios API calls to backend
│   │   ├── App.jsx                # Main app component
│   │   ├── index.css              # Global styles
│   │   └── main.jsx              # React entry point
│   ├── index.html                 # HTML template
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── postcss.config.js          # PostCSS configuration
│   ├── package.json               # Node.js dependencies
│   ├── vite.config.js             # Vite configuration
│   └── .gitignore                 # Ignores node_modules, etc.
│
├── .gitignore                     # Global ignore (optional)
├── README.md                      # 📘 This file
```

## Features

- **Home Page**: Welcomes users and provides an overview of the application.
- **PDF Upload and Preview**: Upload PDFs via the Upload page with real-time previews.
- **Results Display**: View extracted PDF outlines (title and headings) on the Results page.
- **Flask Backend**: Processes PDFs with endpoints for single and batch processing.
- **Responsive UI**: Built with React and styled with Tailwind CSS for a modern, responsive design.
- **Error Handling**: Validates file types, sizes (max 50MB), and page counts (max 50 pages).
- **Logging**: Detailed backend logs for debugging and monitoring.
- **Optional Batch Processing**: Supports processing multiple PDFs in a Docker environment.

## Prerequisites

- **Python 3.8+**: For the Flask backend.
- **Node.js 16+**: For the React frontend.
- **Docker**: Optional, for containerized deployment.
- **Git**: For cloning the repository.

## Setup Instructions

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   Example `requirements.txt`:
   ```txt
   flask==2.3.2
   flask-cors==4.0.0
   werkzeug==2.3.6
   pymupdf==1.22.5
   ```

4. **Ensure pdf_extractor.py:**

   Verify that `app/pdf_extractor.py` contains the `PDFHeadingExtractor` class with a `process_pdf` method (or update `app.py` to use the correct class/method).

5. **Run the backend:**
   ```bash
   python app.py
   ```

   The Flask API will start at `http://localhost:5000`.
   Test the health endpoint: `curl http://localhost:5000/health`.

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

   Key dependencies in `package.json`:
   ```json
   {
     "dependencies": {
       "axios": "^1.4.0",
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "react-hot-toast": "^2.4.1",
       "lucide-react": "^0.263.0",
       "react-router-dom": "^6.14.2",
       "tailwindcss": "^3.3.3"
     }
   }
   ```

3. **Run the frontend:**
   ```bash
   npm run dev
   ```

   The React app will start at `http://localhost:3000` (or the port specified in `vite.config.js`).

### Docker Setup (Optional)

1. **Build and run with Docker Compose:**
   ```bash
   cd backend
   docker-compose up --build
   ```

   Assumes `dockerfile` and `docker-compose.yml` are configured.
   The backend will be available at `http://localhost:5000`.

2. **Batch Processing:**
   - Place PDFs in `backend/app/input`.
   - Call `POST http://localhost:5000/batch-process` to process all PDFs and save JSON outputs to `backend/app/output`.

## Usage

### Access the App:
- Open `http://localhost:3000` to view the Home page.
- Navigate to `/upload` to upload a PDF (max 50MB, 50 pages).
- After uploading, view the extracted outline on the `/results` page.

### Backend Processing:
- PDFs are saved temporarily to `backend/app/input` with unique filenames.
- The `PDFHeadingExtractor` processes the PDF to extract the title and outline.
- Files are deleted after processing (configurable via `CLEANUP_AFTER_PROCESSING`).

### View Results:
- The Upload page shows a PDF preview and initiates extraction.
- The Results page displays the extracted outline (title and headings with levels and page numbers).
- Errors (e.g., invalid PDF, file too large) are shown via toast notifications.

### API Endpoints:
- `GET /health`: Check API status.
- `POST /extract`: Upload and process a single PDF (form field: `pdf`).
- `POST /analyze-documents`: Analyze multiple PDFs with persona-driven logic (optional).
- `POST /batch-process`: Process all PDFs in `app/input` (Docker-friendly).

## Development Notes

### Backend:
- The `app.py` script uses Flask with CORS enabled for frontend integration.
- PDFs are validated for type, size, and page count using PyMuPDF.
- Logs are saved to `app.log` for debugging.

### Frontend:
- Built with Vite for fast development.
- Uses Tailwind CSS for styling and `react-hot-toast` for notifications.
- Pages: `Home.jsx` (landing), `Upload.jsx` (upload and preview), `Results.jsx` (outline display).

### Customization:
- Modify `pdf_extractor.py` to adjust heading extraction logic (e.g., use font sizes or ML-based extraction).
- Add tests to `test_validation.py` for unit testing the extractor.

## Troubleshooting

### ImportError in app.py:
- Ensure `pdf_extractor.py` defines `PDFHeadingExtractor` with `process_pdf`.
- Check the import: `from pdf_extractor import PDFHeadingExtractor`.
- Verify `pymupdf` is installed: `pip install pymupdf`.

### CORS Issues:
- The backend includes `flask-cors`. Restrict origins in production (`CORS(app, origins=['http://localhost:3000'])`).

### File Not Saved:
- Check write permissions for `backend/app/input`.
- Verify logs in `app.log` for file-saving errors.

### Frontend Errors:
- Ensure the backend is running at `http://localhost:5000`.
- Check browser console for Axios errors.

## Future Improvements

- Enhance the Home page with feature highlights or tutorials.
- Add multi-file upload support to the Upload page.
- Improve the Results page with interactive outline navigation.
- Implement authentication for secure uploads.
- Optimize batch processing for large-scale deployments.

## Contributors

[Your Name/Team Name] - Hackathon team for Smart-PDF-Insight.

## License

MIT License - feel free to use and modify for your needs.
