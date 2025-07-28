from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
import tempfile
import shutil
import uuid
import fitz  # PyMuPDF
from pdf_extractor import PDFHeadingExtractor

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
UPLOAD_FOLDER = 'app/input'
OUTPUT_FOLDER = 'app/output'
ALLOWED_EXTENSIONS = {'pdf'}
CLEANUP_AFTER_PROCESSING = True  # Set to False for debugging

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

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(original_filename):
    """Generate a unique filename to prevent conflicts"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(secure_filename(original_filename))
    return f"{timestamp}_{unique_id}_{name}{ext}"

def validate_pdf_file(file_path):
    """Validate PDF file (non-empty, within page limit)"""
    try:
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
        'service': 'PDF Extractor API'
    })

@app.route('/extract', methods=['POST'])
def extract_outline():
    """Extract structured outline from PDF (matches Upload.jsx)"""
    try:
        if 'pdf' not in request.files:
            logger.warning("Request missing 'pdf' file field")
            return jsonify({'error': 'No file provided', 'message': 'Please upload a PDF file using the "pdf" field'}), 400
        
        file = request.files['pdf']
        if file.filename == '':
            logger.warning("Empty filename in request")
            return jsonify({'error': 'No file selected', 'message': 'Please select a PDF file to upload'}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type', 'message': 'Only PDF files are allowed'}), 400
        
        # Generate unique filename and save file
        unique_filename = generate_unique_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        logger.info(f"Saving uploaded file: {file.filename} -> {unique_filename}")
        file.save(filepath)
        
        # Validate PDF file
        is_valid, validation_error = validate_pdf_file(filepath)
        if not is_valid:
            logger.error(f"PDF validation failed: {validation_error}")
            if CLEANUP_AFTER_PROCESSING:
                os.remove(filepath)
            return jsonify({'error': 'Invalid PDF', 'message': validation_error}), 400
        
        # Extract outline
        extractor = PDFExtractor()
        result = extractor.extract_outline(filepath)
        
        # Validate result
        if not result or 'title' not in result or 'outline' not in result:
            logger.error("PDF extraction returned invalid result")
            if CLEANUP_AFTER_PROCESSING:
                os.remove(filepath)
            return jsonify({'error': 'Extraction failed', 'message': 'Failed to extract headings from the PDF'}), 500
        
        # Log extraction statistics
        heading_count = len(result.get('outline', []))
        logger.info(f"Extraction successful: {heading_count} headings found")
        
        # Prepare response
        response = {
            'title': result['title'],
            'outline': result['outline'],
            'metadata': {
                'total_headings': heading_count,
                'original_filename': file.filename,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        # Clean up uploaded file
        if CLEANUP_AFTER_PROCESSING:
            os.remove(filepath)
            logger.info(f"Cleaned up file: {filepath}")
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Unexpected error during processing: {str(e)}")
        if filepath and os.path.exists(filepath) and CLEANUP_AFTER_PROCESSING:
            os.remove(filepath)
        return jsonify({'error': 'Processing failed', 'message': str(e)}), 500

@app.route('/analyze-documents', methods=['POST'])
def analyze_documents():
    """Persona-driven document intelligence"""
    try:
        persona = request.form.get('persona')
        job_to_be_done = request.form.get('job_to_be_done')
        
        if not persona or not job_to_be_done:
            return jsonify({'error': 'Persona and job-to-be-done are required'}), 400
        
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({'error': 'No files provided'}), 400
        
        if len(files) > 10:
            return jsonify({'error': 'Maximum 10 files allowed'}), 400
        
        temp_dir = tempfile.mkdtemp()
        file_paths = []
        
        try:
            for file in files:
                if allowed_file(file.filename):
                    filename = generate_unique_filename(file.filename)
                    filepath = os.path.join(temp_dir, filename)
                    file.save(filepath)
                    file_paths.append(filepath)
            
            if not file_paths:
                return jsonify({'error': 'No valid PDF files found'}), 400
            
            extractor = PDFExtractor()
            result = extractor.analyze_documents(file_paths, persona, job_to_be_done)
            
            return jsonify(result)
        
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/batch-process', methods=['POST'])
def batch_process():
    """Batch processing for Docker environment"""
    try:
        input_dir = UPLOAD_FOLDER
        output_dir = OUTPUT_FOLDER
        
        if not os.path.exists(input_dir):
            return jsonify({'error': 'Input directory not found'}), 404
        
        extractor = PDFExtractor()
        processed_files = []
        
        for filename in os.listdir(input_dir):
            if filename.lower().endswith('.pdf'):
                input_path = os.path.join(input_dir, filename)
                output_filename = filename.replace('.pdf', '.json')
                output_path = os.path.join(output_dir, output_filename)
                
                try:
                    result = extractor.extract_outline(input_path)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    processed_files.append({
                        'input': filename,
                        'output': output_filename,
                        'status': 'success'
                    })
                    
                except Exception as e:
                    processed_files.append({
                        'input': filename,
                        'output': output_filename,
                        'status': 'error',
                        'error': str(e)
                    })
        
        return jsonify({
            'message': f'Processed {len(processed_files)} files',
            'files': processed_files
        })
    
    except Exception as e:
        return jsonify({'error': f'Batch processing failed: {str(e)}'}), 500

@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors"""
    return jsonify({
        'error': 'File too large',
        'message': 'The uploaded file exceeds the maximum size limit of 50MB'
    }), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/extract', '/health', '/analyze-documents', '/batch-process']
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
    logger.info("Starting PDF Extractor API")
    logger.info(f"Upload folder: {UPLOAD_FOLDER}")
    logger.info(f"Max file size: {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)}MB")
    logger.info(f"Cleanup after processing: {CLEANUP_AFTER_PROCESSING}")
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)
