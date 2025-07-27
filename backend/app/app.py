#!/usr/bin/env python3
"""
Flask API for PDF Heading Extraction
Integrates with PDFHeadingExtractor class from pdf_extractor.py
"""

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import os
import uuid
import time
import logging
from datetime import datetime
from pdf_extractor import PDFHeadingExtractor

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'app/input'
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['CLEANUP_AFTER_PROCESSING'] = True  # Set to False to keep files for debugging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize PDF extractor
pdf_extractor = PDFHeadingExtractor()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(secure_filename(original_filename))
    return f"{timestamp}_{unique_id}_{name}{ext}"

def cleanup_file(file_path):
    """Safely delete a file"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to cleanup file {file_path}: {str(e)}")

def validate_pdf_file(file_path):
    """Basic validation to ensure the file is a valid PDF"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        page_count = len(doc)
        doc.close()
        
        if page_count == 0:
            return False, "PDF file appears to be empty"
        
        if page_count > 50:
            return False, f"PDF has {page_count} pages, exceeding the 50-page limit"
        
        return True, None
    except Exception as e:
        return False, f"Invalid PDF file: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'PDF Heading Extractor API'
    })

@app.route('/extract', methods=['POST'])
def extract_headings():
    """
    Extract headings from uploaded PDF file
    
    Expected input: multipart/form-data with 'pdf' field containing the PDF file
    Returns: JSON with title and outline structure
    """
    start_time = time.time()
    uploaded_file_path = None
    
    try:
        # Check if request has file part
        if 'pdf' not in request.files:
            logger.warning("Request missing 'pdf' file field")
            return jsonify({
                'error': 'No file provided',
                'message': 'Please upload a PDF file using the "pdf" field'
            }), 400
        
        file = request.files['pdf']
        
        # Check if file was actually selected
        if file.filename == '':
            logger.warning("Empty filename in request")
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a PDF file to upload'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({
                'error': 'Invalid file type',
                'message': 'Only PDF files are allowed'
            }), 400
        
        # Generate unique filename and save file
        unique_filename = generate_unique_filename(file.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        logger.info(f"Saving uploaded file: {file.filename} -> {unique_filename}")
        file.save(uploaded_file_path)
        
        # Validate PDF file
        is_valid, validation_error = validate_pdf_file(uploaded_file_path)
        if not is_valid:
            logger.error(f"PDF validation failed: {validation_error}")
            return jsonify({
                'error': 'Invalid PDF',
                'message': validation_error
            }), 400
        
        # Process PDF with heading extractor
        logger.info(f"Processing PDF: {unique_filename}")
        processing_start = time.time()
        
        result = pdf_extractor.process_pdf(uploaded_file_path)
        
        processing_time = time.time() - processing_start
        logger.info(f"PDF processing completed in {processing_time:.2f} seconds")
        
        # Validate extraction result
        if not result or 'title' not in result or 'outline' not in result:
            logger.error("PDF extraction returned invalid result")
            return jsonify({
                'error': 'Extraction failed',
                'message': 'Failed to extract headings from the PDF'
            }), 500
        
        # Log extraction statistics
        heading_count = len(result.get('outline', []))
        logger.info(f"Extraction successful: {heading_count} headings found")
        
        # Prepare response
        response = {
            'title': result['title'],
            'outline': result['outline'],
            'metadata': {
                'processing_time': round(processing_time, 2),
                'total_headings': heading_count,
                'original_filename': file.filename,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        total_time = time.time() - start_time
        logger.info(f"Request completed in {total_time:.2f} seconds")
        
        return jsonify(response)
    
    except RequestEntityTooLarge:
        logger.error("File too large")
        return jsonify({
            'error': 'File too large',
            'message': 'PDF file exceeds the maximum size limit of 50MB'
        }), 413
    
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        return jsonify({
            'error': 'Processing failed',
            'message': 'An unexpected error occurred while processing the PDF'
        }), 500
    
    finally:
        # Cleanup uploaded file if configured to do so
        if uploaded_file_path and app.config['CLEANUP_AFTER_PROCESSING']:
            cleanup_file(uploaded_file_path)

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get API usage statistics"""
    upload_dir = app.config['UPLOAD_FOLDER']
    
    stats = {
        'upload_directory': upload_dir,
        'directory_exists': os.path.exists(upload_dir),
        'cleanup_enabled': app.config['CLEANUP_AFTER_PROCESSING'],
        'max_file_size_mb': app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
        'allowed_extensions': list(app.config['ALLOWED_EXTENSIONS']),
        'timestamp': datetime.now().isoformat()
    }
    
    # Count files in upload directory (if cleanup is disabled)
    if os.path.exists(upload_dir):
        files = [f for f in os.listdir(upload_dir) if f.endswith('.pdf')]
        stats['files_in_upload_dir'] = len(files)
    
    return jsonify(stats)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors"""
    return jsonify({
        'error': 'File too large',
        'message': 'The uploaded file exceeds the maximum size limit'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/extract', '/health', '/stats']
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred on the server'
    }), 500

if __name__ == '__main__':
    # Development server configuration
    logger.info("Starting PDF Heading Extractor API")
    logger.info(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    logger.info(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)}MB")
    logger.info(f"Cleanup after processing: {app.config['CLEANUP_AFTER_PROCESSING']}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',  # Accept connections from any IP
        port=5000,       # Default Flask port
        debug=False,     # Set to True for development
        threaded=True    # Enable threading for concurrent requests
    )