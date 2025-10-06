"""
Flask API server for StealthOCR - GitHub Pages compatible
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import base64
import io
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for GitHub Pages

# Initialize OCR
ocr = StealthOCR()

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/api/status', methods=['GET'])
def status():
    """Check API status"""
    return jsonify({
        'status': 'running',
        'message': 'StealthOCR API is operational',
        'engines': ['tesseract', 'easyocr']
    })

@app.route('/api/ocr', methods=['POST'])
def extract_text():
    """Extract text from uploaded PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Get parameters
        engine = request.form.get('engine', 'tesseract')
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.save(tmp_file.name)
            temp_pdf_path = tmp_file.name
        
        try:
            # Convert PDF to images
            logger.info("Converting PDF to images...")
            images = convert_from_path(temp_pdf_path, dpi=300)
            logger.info(f"Converted to {len(images)} pages")
            
            all_text = []
            total_pages = len(images)
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1}/{total_pages}...")
                
                # Convert PIL image to OpenCV format
                img_array = np.array(image)
                if len(img_array.shape) == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Extract text from the page
                page_text = ocr.extract_text(img_array, engine=engine)
                
                if page_text.strip():
                    all_text.append(f"=== PAGE {i+1} ===\n{page_text}\n")
                    logger.info(f"Extracted {len(page_text)} characters from page {i+1}")
                else:
                    logger.info(f"No text found on page {i+1}")
            
            # Combine all text
            full_text = "\n".join(all_text)
            
            # Clean up temporary file
            os.unlink(temp_pdf_path)
            
            return jsonify({
                'success': True,
                'text': full_text,
                'engine': engine,
                'filename': file.filename,
                'pages_processed': total_pages,
                'character_count': len(full_text),
                'word_count': len(full_text.split())
            })
        
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            raise e
    
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/ocr/base64', methods=['POST'])
def extract_text_base64():
    """Extract text from base64 encoded PDF"""
    try:
        data = request.get_json()
        
        if 'pdf_data' not in data:
            return jsonify({'error': 'No PDF data provided'}), 400
        
        engine = data.get('engine', 'tesseract')
        
        # Decode base64 PDF
        pdf_data = base64.b64decode(data['pdf_data'])
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_data)
            temp_pdf_path = tmp_file.name
        
        try:
            # Convert PDF to images
            images = convert_from_path(temp_pdf_path, dpi=300)
            
            all_text = []
            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                img_array = np.array(image)
                if len(img_array.shape) == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Extract text from the page
                page_text = ocr.extract_text(img_array, engine=engine)
                if page_text.strip():
                    all_text.append(f"=== PAGE {i+1} ===\n{page_text}\n")
            
            # Combine all text
            full_text = "\n".join(all_text)
            
            # Clean up temporary file
            os.unlink(temp_pdf_path)
            
            return jsonify({
                'success': True,
                'text': full_text,
                'engine': engine,
                'pages_processed': len(images),
                'character_count': len(full_text),
                'word_count': len(full_text.split())
            })
        
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
            raise e
    
    except Exception as e:
        logger.error(f"Error processing base64 PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=5000)