"""
AWS Lambda function for StealthOCR PDF processing
"""

import json
import base64
import tempfile
import os
import sys
from io import BytesIO
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Add the src directory to the path
sys.path.append('/opt/python/src')

try:
    from stealth_ocr import StealthOCR
    from pdf2image import convert_from_path
    import cv2
    import numpy as np
    from PIL import Image
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

# Initialize OCR (this will be done once per container)
ocr = None

def init_ocr():
    """Initialize OCR engine"""
    global ocr
    if ocr is None:
        try:
            ocr = StealthOCR()
            logger.info("OCR engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OCR: {e}")
            raise

def lambda_handler(event, context):
    """
    AWS Lambda handler for PDF OCR processing
    
    Expected event structure:
    {
        "httpMethod": "POST",
        "body": "base64_encoded_pdf_data",
        "headers": {
            "Content-Type": "application/json"
        },
        "queryStringParameters": {
            "engine": "tesseract"  # optional
        }
    }
    """
    
    # Initialize OCR if not already done
    init_ocr()
    
    try:
        # Parse the event
        http_method = event.get('httpMethod', '')
        
        if http_method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
        
        # Handle CORS preflight
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type'
                },
                'body': ''
            }
        
        # Parse request body
        try:
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event.get('body', {})
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
        
        # Get PDF data
        pdf_data = body.get('pdf_data')
        if not pdf_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No PDF data provided'})
            }
        
        # Get engine parameter
        engine = event.get('queryStringParameters', {}).get('engine', 'tesseract')
        
        # Decode base64 PDF data
        try:
            pdf_bytes = base64.b64decode(pdf_data)
        except Exception as e:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': f'Invalid base64 data: {str(e)}'})
            }
        
        # Process PDF
        result = process_pdf(pdf_bytes, engine)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda execution error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': f'Internal server error: {str(e)}'})
        }

def process_pdf(pdf_bytes, engine='tesseract'):
    """
    Process PDF and extract text using OCR
    
    Args:
        pdf_bytes: PDF file as bytes
        engine: OCR engine to use ('tesseract' or 'easyocr')
    
    Returns:
        Dictionary with extraction results
    """
    temp_pdf_path = None
    
    try:
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            temp_pdf_path = tmp_file.name
        
        logger.info("Converting PDF to images...")
        
        # Convert PDF to images
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
        
        # Calculate statistics
        word_count = len(full_text.split()) if full_text else 0
        char_count = len(full_text)
        
        return {
            'success': True,
            'text': full_text,
            'engine': engine,
            'pages_processed': total_pages,
            'character_count': char_count,
            'word_count': word_count,
            'line_count': len(full_text.split('\n')) if full_text else 0
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'text': '',
            'pages_processed': 0,
            'character_count': 0,
            'word_count': 0,
            'line_count': 0
        }
    
    finally:
        # Clean up temporary file
        if temp_pdf_path and os.path.exists(temp_pdf_path):
            try:
                os.unlink(temp_pdf_path)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")

# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "httpMethod": "POST",
        "body": json.dumps({
            "pdf_data": "base64_encoded_pdf_here"
        }),
        "queryStringParameters": {
            "engine": "tesseract"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))