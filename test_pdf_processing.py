"""
Test script for PDF processing with the provided PDF file
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import base64
import json
import time

def test_pdf_processing():
    """Test PDF processing with the provided file"""
    
    pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    
    print("StealthOCR PDF Processing Test")
    print("=" * 40)
    
    # Check if PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return False
    
    print(f"Testing with: {os.path.basename(pdf_path)}")
    print(f"File size: {os.path.getsize(pdf_path) / (1024*1024):.2f} MB")
    
    # Initialize OCR
    print("\nInitializing OCR engine...")
    ocr = StealthOCR()
    
    try:
        # Convert PDF to images
        print("Converting PDF to images...")
        start_time = time.time()
        images = convert_from_path(pdf_path, dpi=300)
        conversion_time = time.time() - start_time
        
        print(f"Converted to {len(images)} pages in {conversion_time:.2f} seconds")
        
        # Process each page
        all_text = []
        total_processing_time = 0
        
        for i, image in enumerate(images):
            print(f"\nProcessing page {i+1}/{len(images)}...")
            page_start = time.time()
            
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Extract text using Tesseract
            page_text = ocr.extract_text(img_array, engine='tesseract')
            page_time = time.time() - page_start
            total_processing_time += page_time
            
            if page_text.strip():
                all_text.append(f"=== PAGE {i+1} ===\n{page_text}\n")
                print(f"✓ Extracted {len(page_text)} characters in {page_time:.2f}s")
            else:
                print(f"⚠ No text found on page {i+1}")
        
        # Combine all text
        full_text = "\n".join(all_text)
        
        # Calculate statistics
        word_count = len(full_text.split()) if full_text else 0
        char_count = len(full_text)
        line_count = len(full_text.split('\n')) if full_text else 0
        
        print(f"\n" + "="*50)
        print("PROCESSING RESULTS")
        print("="*50)
        print(f"Total pages processed: {len(images)}")
        print(f"Total characters extracted: {char_count:,}")
        print(f"Total words extracted: {word_count:,}")
        print(f"Total lines extracted: {line_count:,}")
        print(f"Conversion time: {conversion_time:.2f}s")
        print(f"OCR processing time: {total_processing_time:.2f}s")
        print(f"Total time: {conversion_time + total_processing_time:.2f}s")
        
        # Show sample text
        print(f"\n" + "="*50)
        print("SAMPLE EXTRACTED TEXT (first 1000 characters)")
        print("="*50)
        print(full_text[:1000])
        if len(full_text) > 1000:
            print(f"\n... (showing first 1000 characters of {len(full_text):,} total)")
        
        # Test base64 encoding for Lambda
        print(f"\n" + "="*50)
        print("LAMBDA COMPATIBILITY TEST")
        print("="*50)
        
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        base64_data = base64.b64encode(pdf_bytes).decode('utf-8')
        print(f"Base64 encoded size: {len(base64_data):,} characters")
        print(f"Base64 size: {len(base64_data) / (1024*1024):.2f} MB")
        
        # Create Lambda request payload
        lambda_payload = {
            "pdf_data": base64_data
        }
        
        payload_size = len(json.dumps(lambda_payload))
        print(f"Lambda payload size: {payload_size:,} characters")
        print(f"Lambda payload size: {payload_size / (1024*1024):.2f} MB")
        
        # Check Lambda payload size limit (6MB)
        if payload_size > 6 * 1024 * 1024:
            print("⚠ WARNING: Payload exceeds Lambda 6MB limit!")
        else:
            print("✓ Payload within Lambda 6MB limit")
        
        # Save results
        output_file = "extracted_text.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        print(f"\n✓ Results saved to: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing PDF: {e}")
        return False

def test_lambda_simulation():
    """Simulate Lambda function processing"""
    print(f"\n" + "="*50)
    print("LAMBDA SIMULATION TEST")
    print("="*50)
    
    pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    
    try:
        # Read PDF and encode as base64
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        base64_data = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Simulate Lambda event
        event = {
            "httpMethod": "POST",
            "body": json.dumps({
                "pdf_data": base64_data
            }),
            "queryStringParameters": {
                "engine": "tesseract"
            }
        }
        
        # Import and test Lambda function
        from lambda_function import lambda_handler
        
        print("Simulating Lambda function...")
        start_time = time.time()
        
        result = lambda_handler(event, None)
        
        processing_time = time.time() - start_time
        
        print(f"Lambda processing time: {processing_time:.2f}s")
        print(f"Status code: {result['statusCode']}")
        
        if result['statusCode'] == 200:
            response_body = json.loads(result['body'])
            print(f"Success: {response_body['success']}")
            print(f"Pages processed: {response_body['pages_processed']}")
            print(f"Characters extracted: {response_body['character_count']:,}")
            print(f"Words extracted: {response_body['word_count']:,}")
            
            # Show sample text
            text = response_body['text']
            print(f"\nSample text (first 500 characters):")
            print("-" * 50)
            print(text[:500])
            if len(text) > 500:
                print(f"\n... (showing first 500 characters of {len(text):,} total)")
        else:
            print(f"Error: {result['body']}")
        
        return result['statusCode'] == 200
        
    except Exception as e:
        print(f"❌ Lambda simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting StealthOCR PDF Processing Tests...")
    
    # Test 1: Direct PDF processing
    success1 = test_pdf_processing()
    
    # Test 2: Lambda simulation
    success2 = test_lambda_simulation()
    
    print(f"\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Direct PDF processing: {'✓ PASS' if success1 else '❌ FAIL'}")
    print(f"Lambda simulation: {'✓ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Ready for deployment.")
    else:
        print("\n⚠ Some tests failed. Check the errors above.")