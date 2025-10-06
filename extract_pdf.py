"""
PDF Text Extraction Script for StealthOCR
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import argparse


def extract_text_from_pdf(pdf_path, output_file=None, engine='tesseract'):
    """
    Extract text from PDF using OCR
    
    Args:
        pdf_path: Path to the PDF file
        output_file: Optional output file to save extracted text
        engine: OCR engine to use ('tesseract' or 'easyocr')
    
    Returns:
        Extracted text
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Initialize OCR
    ocr = StealthOCR()
    
    try:
        # Convert PDF to images
        print("Converting PDF to images...")
        images = convert_from_path(pdf_path, dpi=300)  # High DPI for better OCR
        print(f"Converted to {len(images)} pages")
        
        all_text = []
        
        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}...")
            
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Extract text from the page
            page_text = ocr.extract_text(img_array, engine=engine)
            
            if page_text.strip():
                all_text.append(f"=== PAGE {i+1} ===\n{page_text}\n")
                print(f"Extracted {len(page_text)} characters from page {i+1}")
            else:
                print(f"No text found on page {i+1}")
        
        # Combine all text
        full_text = "\n".join(all_text)
        
        # Save to file if specified
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_text)
            print(f"Text saved to: {output_file}")
        
        return full_text
    
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(description='Extract text from PDF using StealthOCR')
    parser.add_argument('pdf_path', help='Path to the PDF file')
    parser.add_argument('-o', '--output', help='Output file to save extracted text')
    parser.add_argument('-e', '--engine', choices=['tesseract', 'easyocr'], 
                       default='tesseract', help='OCR engine to use')
    
    args = parser.parse_args()
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        print(f"Error: PDF file not found: {args.pdf_path}")
        return
    
    # Extract text
    text = extract_text_from_pdf(args.pdf_path, args.output, args.engine)
    
    if text:
        print(f"\nExtracted {len(text)} characters total")
        print("\n" + "="*50)
        print("EXTRACTED TEXT:")
        print("="*50)
        print(text[:2000])  # Show first 2000 characters
        if len(text) > 2000:
            print(f"\n... (showing first 2000 characters of {len(text)} total)")
    else:
        print("No text was extracted from the PDF")


if __name__ == "__main__":
    main()