"""
PDF Text Extraction to CSV Script for StealthOCR
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from stealth_ocr import StealthOCR
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import csv
import re
from datetime import datetime


def clean_text_for_csv(text):
    """Clean text for CSV formatting"""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might break CSV
    text = text.replace('"', '""')  # Escape quotes
    text = text.replace('\n', ' ')  # Replace newlines with spaces
    text = text.replace('\r', ' ')  # Replace carriage returns
    return text.strip()


def extract_pdf_to_csv(pdf_path, csv_path, engine='tesseract'):
    """
    Extract text from PDF and save to CSV
    
    Args:
        pdf_path: Path to the PDF file
        csv_path: Path to the CSV output file
        engine: OCR engine to use ('tesseract' or 'easyocr')
    """
    print(f"Processing PDF: {pdf_path}")
    print(f"Output CSV: {csv_path}")
    
    # Initialize OCR
    ocr = StealthOCR()
    
    try:
        # Convert PDF to images
        print("Converting PDF to images...")
        images = convert_from_path(pdf_path, dpi=300)  # High DPI for better OCR
        print(f"Converted to {len(images)} pages")
        
        # Prepare CSV data
        csv_data = []
        csv_data.append(['Page', 'Text', 'Character_Count', 'Word_Count', 'Extraction_Time'])
        
        total_text = ""
        
        for i, image in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}...")
            start_time = datetime.now()
            
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            # Extract text from the page
            page_text = ocr.extract_text(img_array, engine=engine)
            end_time = datetime.now()
            extraction_time = (end_time - start_time).total_seconds()
            
            if page_text.strip():
                # Clean text for CSV
                clean_text = clean_text_for_csv(page_text)
                word_count = len(clean_text.split())
                
                # Add to CSV data
                csv_data.append([
                    i + 1,
                    clean_text,
                    len(clean_text),
                    word_count,
                    f"{extraction_time:.2f}s"
                ])
                
                total_text += clean_text + " "
                print(f"Extracted {len(clean_text)} characters, {word_count} words from page {i+1}")
            else:
                csv_data.append([i + 1, "", 0, 0, f"{extraction_time:.2f}s"])
                print(f"No text found on page {i+1}")
        
        # Add summary row
        total_words = len(total_text.split())
        csv_data.append(['SUMMARY', 'Total extracted text', len(total_text), total_words, ''])
        
        # Write to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(csv_data)
        
        print(f"\nCSV file saved to: {csv_path}")
        print(f"Total pages processed: {len(images)}")
        print(f"Total characters extracted: {len(total_text)}")
        print(f"Total words extracted: {total_words}")
        
        return total_text
    
    except Exception as e:
        print(f"Error processing PDF: {e}")
        return ""


def main():
    pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    csv_path = "/Users/danielmcshan/Downloads/FY25 Extract - Sheet1 (2).csv"
    
    # Check if PDF file exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return
    
    print("StealthOCR PDF to CSV Extractor")
    print("=" * 40)
    
    # Extract text and save to CSV
    text = extract_pdf_to_csv(pdf_path, csv_path, engine='tesseract')
    
    if text:
        print("\nExtraction completed successfully!")
        print(f"First 500 characters preview:")
        print("-" * 50)
        print(text[:500])
        if len(text) > 500:
            print(f"\n... (showing first 500 characters of {len(text)} total)")
    else:
        print("No text was extracted from the PDF")


if __name__ == "__main__":
    main()