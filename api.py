"""
Flask API for StealthOCR
"""

from flask import Flask, request, jsonify
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
import cv2
import numpy as np
from PIL import Image
import base64
import io

app = Flask(__name__)

# Initialize OCR
ocr = StealthOCR()


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
    """Extract text from uploaded image"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get parameters
        engine = request.form.get('engine', 'tesseract')
        
        # Read image
        image = Image.open(file.stream)
        img_array = np.array(image)
        
        # Convert to OpenCV format
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Extract text
        text = ocr.extract_text(img_array, engine=engine)
        
        return jsonify({
            'success': True,
            'text': text,
            'engine': engine,
            'filename': file.filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ocr/base64', methods=['POST'])
def extract_text_base64():
    """Extract text from base64 encoded image"""
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        engine = data.get('engine', 'tesseract')
        
        # Decode base64 image
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))
        img_array = np.array(image)
        
        # Convert to OpenCV format
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Extract text
        text = ocr.extract_text(img_array, engine=engine)
        
        return jsonify({
            'success': True,
            'text': text,
            'engine': engine
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/batch', methods=['POST'])
def batch_process():
    """Process multiple images"""
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        
        files = request.files.getlist('files')
        engine = request.form.get('engine', 'tesseract')
        
        results = {}
        
        for file in files:
            if file.filename == '':
                continue
            
            try:
                # Read image
                image = Image.open(file.stream)
                img_array = np.array(image)
                
                # Convert to OpenCV format
                if len(img_array.shape) == 3:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Extract text
                text = ocr.extract_text(img_array, engine=engine)
                results[file.filename] = text
                
            except Exception as e:
                results[file.filename] = f"Error: {str(e)}"
        
        return jsonify({
            'success': True,
            'results': results,
            'engine': engine,
            'processed_count': len(results)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/confidence', methods=['POST'])
def get_confidence():
    """Get confidence scores for OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        # Read image
        image = Image.open(file.stream)
        img_array = np.array(image)
        
        # Convert to OpenCV format
        if len(img_array.shape) == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Get confidence scores
        confidence = ocr.get_text_confidence(img_array)
        
        return jsonify({
            'success': True,
            'confidence': confidence,
            'filename': file.filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)