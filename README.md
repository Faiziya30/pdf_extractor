pdf_extractor
pdf_extractor is a web application designed to extract structured outlines from PDF documents. The project features a Flask-based backend that processes uploaded PDFs and a React frontend with Tailwind CSS for a seamless user experience. Users can upload PDFs, view previews, and receive extracted headings in an organized format, making it ideal for document analysis and summarization.
Project Structure
pdf_extractor/
│
├── backend/                        # 🔙 Flask app
│   ├── app/
│   │   ├── input/                 # ⬆ Uploaded PDFs go here temporarily
│   │   ├── output/                # 📤 Stores JSON outputs (optional for batch processing)
│   │   ├── __pycache__/
│   │   ├── pdf_extractor.py       # 🧠 PDF extraction logic
│   │   └── test_validation.py     # ✅ Unit tests 
│   ├── app.py                     # 🚀 Flask API entry point
│   ├── requirements.txt           # 📦 Python dependencies
│   ├── dockerfile                 # 🐳 Docker configuration 
│   ├── docker-compose.yml         # 🐳 Local testing setup 
│   └── .gitignore                 # ❌ Ignores venv, __pycache__, etc.
│
├── frontend/                      # 🎨 React App
│   ├── public/                    # Static assets
│   ├── src/
│   │   ├── assets/                # Images, fonts, etc.
│   │   ├── components/            # Reusable React components
│   │   ├── pages/
│   │   │   └── Upload.jsx         # 📤 PDF upload and result display
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

Features

PDF Upload and Preview: Upload PDFs via a user-friendly React interface with real-time previews.
Heading Extraction: Extracts structured outlines (title and headings) from PDFs using PyMuPDF.
Flask Backend: Handles PDF uploads, validation, and processing with endpoints for single and batch processing.
Responsive UI: Built with React and styled with Tailwind CSS for a modern, responsive design.
Error Handling: Robust validation for file types, sizes (max 50MB), and page counts (max 50 pages).
Logging: Detailed backend logs for debugging and monitoring.
Optional Batch Processing: Supports processing multiple PDFs in a Docker environment.

Prerequisites

Python 3.8+: For the Flask backend.
Node.js 16+: For the React frontend.
Docker: for containerized deployment.
Git: For cloning the repository.

Setup Instructions
Backend Setup

Navigate to the backend directory:
cd backend


Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install dependencies:
pip install -r requirements.txt

Example requirements.txt:
flask==2.3.2
flask-cors==4.0.0
werkzeug==2.3.6
pymupdf==1.22.5


Ensure pdf_extractor.py:

Verify that app/pdf_extractor.py contains the PDFHeadingExtractor class with a process_pdf method (or update app.py to use the correct class/method).


Run the backend:
python app.py


The Flask API will start at http://localhost:5000.




Frontend Setup

Navigate to the frontend directory:
cd frontend


Install dependencies:
npm install

Key dependencies in package.json:
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


Run the frontend:
npm run dev


The React app will start at http://localhost:3000 (or the port specified in vite.config.js).



Docker Setup (Optional)

Build and run with Docker Compose:
cd backend
docker-compose up --build


Assumes dockerfile and docker-compose.yml are configured.
The backend will be available at http://localhost:5000.


Batch Processing:

Place PDFs in backend/app/input.
Call POST http://localhost:5000/batch-process to process all PDFs and save JSON outputs to backend/app/output.



Usage

Access the App:

Open http://localhost:3000/upload in your browser.
Select a PDF file (max 50MB, 50 pages).
Click "Upload & Extract" to send the PDF to the backend.


Backend Processing:

The PDF is saved temporarily to backend/app/input with a unique filename.
The PDFHeadingExtractor processes the PDF to extract the title and outline.
The file is deleted after processing (configurable via CLEANUP_AFTER_PROCESSING).


View Results:

The frontend displays the PDF preview and extracted outline (title and headings with levels and page numbers).
Errors (e.g., invalid PDF, file too large) are shown via toast notifications.


API Endpoints:

GET /health: Check API status.
POST /extract: Upload and process a single PDF (form field: pdf).
POST /analyze-documents: Analyze multiple PDFs with persona-driven logic (optional).
POST /batch-process: Process all PDFs in app/input (Docker-friendly).



Development Notes

Backend:
The app.py script uses Flask with CORS enabled for frontend integration.
PDFs are validated for type, size, and page count using PyMuPDF.
Logs are saved to app.log for debugging.


Frontend:
Built with Vite for fast development.
Uses Tailwind CSS for styling and react-hot-toast for notifications.
The Upload.jsx page handles PDF uploads and displays results.


Customization:
Modify pdf_extractor.py to adjust heading extraction logic (e.g., use font sizes, styles, or ML-based extraction).
Add tests to test_validation.py for unit testing the extractor.



Troubleshooting

ImportError in app.py:
Ensure pdf_extractor.py defines PDFHeadingExtractor (or the expected class).
Check the import path: from pdf_extractor import PDFHeadingExtractor.
Verify pymupdf is installed: pip install pymupdf.


CORS Issues:
The backend includes flask-cors. Restrict origins in production (CORS(app, origins=['http://localhost:3000'])).


File Not Saved:
Check write permissions for backend/app/input.
Verify logs in app.log for file-saving errors.


Frontend Errors:
Ensure the backend is running at http://localhost:5000.
Check browser console for Axios errors.



Future Improvements

Add advanced PDF parsing (e.g., extract text, images, or tables).
Implement authentication for secure uploads.
Enhance the frontend with drag-and-drop support and multi-file uploads.
Optimize batch processing for large-scale deployments.

Contributors

[Faiziya,Rakhi,Ayush]

