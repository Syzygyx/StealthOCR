#!/usr/bin/env python3
"""
Test script for exact CSV format generation
"""

import os
import sys
import pandas as pd
from pathlib import Path

# Add src directory to path
sys.path.append('src')

from stealth_ocr import StealthOCR
from pdf_to_exact_csv_transformer import PDFToExactCSVTransformer

def test_exact_csv_generation(pdf_path):
    """Test exact CSV generation from PDF"""
    print(f"🔍 Testing exact CSV generation from: {pdf_path}")
    
    try:
        from pdf2image import convert_from_path
        import cv2
        import numpy as np
        
        # Initialize StealthOCR
        ocr = StealthOCR()
        
        # Convert PDF to images
        print("   Converting PDF to images...")
        images = convert_from_path(pdf_path)
        
        # Extract text from each page
        all_text = []
        for i, image in enumerate(images):
            print(f"   Processing page {i+1}/{len(images)}...")
            
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Extract text using StealthOCR
            page_text = ocr.extract_text(opencv_image)
            all_text.append(f"=== PAGE {i+1} ===\n{page_text}")
        
        # Combine all text
        combined_text = "\n\n".join(all_text)
        
        # Initialize CSV transformer
        transformer = PDFToExactCSVTransformer()
        
        # Transform to exact CSV format
        csv_file = transformer.transform_ocr_to_csv(
            combined_text, 
            "exact_output.csv",
            pdf_path
        )
        
        print(f"✅ CSV generation successful!")
        print(f"   - Output file: {csv_file}")
        
        # Validate CSV structure
        validate_csv_structure(csv_file)
        
        return csv_file
        
    except Exception as e:
        print(f"❌ CSV generation failed: {e}")
        return None

def validate_csv_structure(csv_file):
    """Validate the CSV structure matches the target format"""
    print(f"🔍 Validating CSV structure...")
    
    try:
        # Read the CSV
        df = pd.read_csv(csv_file)
        
        # Expected columns
        expected_columns = [
            'appropriation_category',
            'appropriation code', 
            'appropriation activity',
            'branch',
            'fiscal_year_start',
            'fiscal_year_end',
            'budget_activity_number',
            'budget_activity_title',
            'pem',
            'budget_title',
            'program_base_congressional',
            'program_base_dod',
            'reprogramming_amount',
            'revised_program_total',
            'explanation',
            'file'
        ]
        
        print(f"   - Rows: {len(df)}")
        print(f"   - Columns: {len(df.columns)}")
        print(f"   - Expected columns: {len(expected_columns)}")
        
        # Check if all expected columns are present
        missing_columns = set(expected_columns) - set(df.columns)
        extra_columns = set(df.columns) - set(expected_columns)
        
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
        else:
            print(f"   ✅ All expected columns present")
        
        if extra_columns:
            print(f"   ⚠️  Extra columns: {extra_columns}")
        
        # Show sample data
        print(f"\n📊 Sample data:")
        print(df.head(3).to_string(index=False))
        
        return len(missing_columns) == 0
        
    except Exception as e:
        print(f"❌ CSV validation failed: {e}")
        return False

def compare_with_target(target_csv, generated_csv):
    """Compare generated CSV with target CSV structure"""
    print(f"🔍 Comparing with target CSV...")
    
    try:
        # Read both CSVs
        target_df = pd.read_csv(target_csv)
        generated_df = pd.read_csv(generated_csv)
        
        print(f"   Target CSV: {len(target_df)} rows, {len(target_df.columns)} columns")
        print(f"   Generated CSV: {len(generated_df)} rows, {len(generated_df.columns)} columns")
        
        # Check column structure
        target_cols = set(target_df.columns)
        generated_cols = set(generated_df.columns)
        
        if target_cols == generated_cols:
            print("   ✅ Column structure matches!")
        else:
            print("   ❌ Column structure differs")
            print(f"   Target columns: {sorted(target_cols)}")
            print(f"   Generated columns: {sorted(generated_cols)}")
        
        return target_cols == generated_cols
        
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        return False

def main():
    """Main test function"""
    print("🔬 StealthOCR Exact CSV Format Test")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('src/stealth_ocr.py'):
        print("❌ Please run this script from the StealthOCR root directory")
        return False
    
    # Test with real PDF
    pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    target_csv = "/Users/danielmcshan/Downloads/FY25 Extract - Sheet1 (2).csv"
    
    if os.path.exists(pdf_path):
        # Generate CSV
        csv_file = test_exact_csv_generation(pdf_path)
        
        if csv_file and os.path.exists(target_csv):
            # Compare with target
            compare_with_target(target_csv, csv_file)
        
        print(f"\n📁 Generated files:")
        print(f"   - {csv_file}")
        
        return csv_file is not None
    else:
        print(f"❌ PDF not found at: {pdf_path}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)