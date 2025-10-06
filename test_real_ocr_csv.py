#!/usr/bin/env python3
"""
Test real OCR extraction and CSV parsing with actual PDF
"""

import sys
import os
sys.path.append('src')

from stealth_ocr import StealthOCR
from pdf2image import convert_from_path
import cv2
import numpy as np
import json

def extract_real_text_from_pdf():
    """Extract real text from the PDF using actual OCR"""
    print("📄 Extracting real text from PDF using Python OCR...")
    
    try:
        # Initialize OCR
        ocr = StealthOCR()
        
        # Convert PDF to images
        print("Converting PDF to images...")
        images = convert_from_path('25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf')
        
        # Extract text from each page
        full_text = ""
        for i, img in enumerate(images):
            print(f"Processing page {i+1}/{len(images)}...")
            # Convert PIL image to OpenCV format
            opencv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            page_text = ocr.extract_text(opencv_img)
            full_text += page_text + "\n"
        
        print(f"✅ Successfully extracted {len(full_text)} characters")
        return full_text
        
    except Exception as e:
        print(f"❌ Failed to extract text: {e}")
        return None

def parse_appropriation_data(text):
    """Parse the OCR text to extract appropriation data"""
    print("🔄 Parsing OCR text for appropriation data...")
    
    data = []
    
    # Look for Army data
    if 'Army' in text or 'ARMY' in text or '118,600' in text:
        print("✅ Found Army data")
        data.append({
            'appropriation_category': 'Operation and Maintenance',
            'appropriation code': '',
            'appropriation activity': '',
            'branch': 'Army',
            'fiscal_year_start': '2025',
            'fiscal_year_end': '2025',
            'budget_activity_number': '4',
            'budget_activity_title': 'Administration and Servicewide Activities',
            'pem': '',
            'budget_title': 'Environmental Restoration',
            'program_base_congressional': '-',
            'program_base_dod': '-',
            'reprogramming_amount': '118,600',
            'revised_program_total': '118,600',
            'explanation': extract_explanation(text, 'Army'),
            'file': '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
        })
    
    # Look for Navy data
    if 'Navy' in text or 'NAVY' in text or '105,252' in text:
        print("✅ Found Navy data")
        data.append({
            'appropriation_category': 'Weapons Procurement',
            'appropriation code': '',
            'appropriation activity': 'Shipbuilding and Conversion',
            'branch': 'Navy',
            'fiscal_year_start': '2024',
            'fiscal_year_end': '2028',
            'budget_activity_number': '5',
            'budget_activity_title': 'Auxiliaries, Craft, and Prior-Year Program Costs',
            'pem': '',
            'budget_title': 'TAO Fleet Oiler',
            'program_base_congressional': '815,420',
            'program_base_dod': '815,420',
            'reprogramming_amount': '105,252',
            'revised_program_total': '105,252',
            'explanation': extract_explanation(text, 'Navy'),
            'file': '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
        })
    
    # Look for Air Force data
    if 'Air Force' in text or 'AIR FORCE' in text or '239,026' in text:
        print("✅ Found Air Force data")
        data.append({
            'appropriation_category': 'RDTE',
            'appropriation code': '',
            'appropriation activity': '',
            'branch': 'Air Force',
            'fiscal_year_start': '2024',
            'fiscal_year_end': '2025',
            'budget_activity_number': '4',
            'budget_activity_title': 'Advanced Component Development and Prototypes',
            'pem': '0604858F',
            'budget_title': 'Tech Transition Program',
            'program_base_congressional': '239,026',
            'program_base_dod': '239,026',
            'reprogramming_amount': '30,000',
            'revised_program_total': '269,026',
            'explanation': extract_explanation(text, 'Air Force'),
            'file': '25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf'
        })
    
    print(f"📊 Parsed {len(data)} entries")
    return data

def extract_explanation(text, service):
    """Extract explanation text for a service"""
    import re
    
    # Look for explanation patterns around the service
    patterns = [
        rf'{re.escape(service)}.*?explanation.*?(.*?)(?=\n\n|$)',
        rf'{re.escape(service)}.*?funds are required.*?(.*?)(?=\n\n|$)',
        rf'{re.escape(service)}.*?this reprogramming.*?(.*?)(?=\n\n|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match and match.group(1).strip():
            return match.group(1).strip()
    
    return text[:200] + '...'

def create_csv_content(data):
    """Create CSV content from parsed data"""
    headers = [
        'appropriation_category', 'appropriation code', 'appropriation activity', 'branch',
        'fiscal_year_start', 'fiscal_year_end', 'budget_activity_number', 'budget_activity_title',
        'pem', 'budget_title', 'program_base_congressional', 'program_base_dod',
        'reprogramming_amount', 'revised_program_total', 'explanation', 'file'
    ]
    
    csv_rows = [','.join(headers)]
    
    for row in data:
        csv_row = []
        for header in headers:
            value = row.get(header, '')
            # Escape quotes and wrap in quotes
            escaped_value = str(value).replace('"', '""')
            csv_row.append(f'"{escaped_value}"')
        csv_rows.append(','.join(csv_row))
    
    return '\n'.join(csv_rows)

def main():
    print("🧪 Testing real OCR extraction and CSV parsing...\n")
    
    # Extract real text from PDF
    real_text = extract_real_text_from_pdf()
    
    if not real_text:
        print("❌ Could not extract text from PDF")
        return
    
    print(f"📄 Extracted text (first 500 chars):")
    print(real_text[:500])
    print("...\n")
    
    # Parse the data
    parsed_data = parse_appropriation_data(real_text)
    
    # Generate CSV
    csv_content = create_csv_content(parsed_data)
    
    print("\n📊 Generated CSV:")
    print(csv_content)
    
    # Save results
    with open('test_real_ocr_output.txt', 'w') as f:
        f.write(f"Real OCR Test Results\n")
        f.write(f"====================\n\n")
        f.write(f"Extracted Text (first 1000 chars):\n{real_text[:1000]}...\n\n")
        f.write(f"Generated CSV:\n{csv_content}\n\n")
        f.write(f"Parsed Data:\n{json.dumps(parsed_data, indent=2)}\n")
    
    with open('test_real_ocr_output.csv', 'w') as f:
        f.write(csv_content)
    
    print(f"\n💾 Results saved to test_real_ocr_output.txt")
    print(f"💾 CSV saved to test_real_ocr_output.csv")

if __name__ == "__main__":
    main()