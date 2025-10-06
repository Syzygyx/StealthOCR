#!/usr/bin/env python3
"""
Validate that generated CSV matches the exact target format
"""

import pandas as pd
import sys
import os

def validate_csv_format(generated_csv, target_csv):
    """Compare generated CSV with target CSV format"""
    print(f"🔍 Validating CSV format...")
    print(f"   Generated: {generated_csv}")
    print(f"   Target: {target_csv}")
    
    try:
        # Read both CSVs
        gen_df = pd.read_csv(generated_csv)
        target_df = pd.read_csv(target_csv)
        
        print(f"\n📊 Structure Comparison:")
        print(f"   Generated: {len(gen_df)} rows, {len(gen_df.columns)} columns")
        print(f"   Target: {len(target_df)} rows, {len(target_df.columns)} columns")
        
        # Check columns
        gen_cols = set(gen_df.columns)
        target_cols = set(target_df.columns)
        
        if gen_cols == target_cols:
            print("   ✅ Column structure matches exactly!")
        else:
            print("   ❌ Column structure differs")
            missing = target_cols - gen_cols
            extra = gen_cols - target_cols
            if missing:
                print(f"   Missing columns: {missing}")
            if extra:
                print(f"   Extra columns: {extra}")
        
        # Check data types and sample values
        print(f"\n📋 Sample Data Comparison:")
        print("Generated CSV sample:")
        print(gen_df.head(2).to_string(index=False))
        
        print("\nTarget CSV sample:")
        print(target_df.head(2).to_string(index=False))
        
        # Check if appropriation data is present
        print(f"\n💰 Appropriation Data Check:")
        if 'appropriation_category' in gen_df.columns:
            categories = gen_df['appropriation_category'].value_counts()
            print(f"   Categories found: {dict(categories)}")
        
        if 'branch' in gen_df.columns:
            branches = gen_df['branch'].value_counts()
            print(f"   Branches found: {dict(branches)}")
        
        if 'reprogramming_amount' in gen_df.columns:
            amounts = gen_df['reprogramming_amount'].dropna()
            print(f"   Reprogramming amounts: {list(amounts)}")
        
        return gen_cols == target_cols
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python validate_csv_format.py <generated_csv> <target_csv>")
        print("Example: python validate_csv_format.py exact_output.csv '/Users/danielmcshan/Downloads/FY25 Extract - Sheet1 (2).csv'")
        return
    
    generated_csv = sys.argv[1]
    target_csv = sys.argv[2]
    
    if not os.path.exists(generated_csv):
        print(f"❌ Generated CSV not found: {generated_csv}")
        return
    
    if not os.path.exists(target_csv):
        print(f"❌ Target CSV not found: {target_csv}")
        return
    
    success = validate_csv_format(generated_csv, target_csv)
    
    if success:
        print("\n🎉 CSV format validation PASSED!")
        print("   The generated CSV matches the target format exactly.")
    else:
        print("\n❌ CSV format validation FAILED!")
        print("   The generated CSV does not match the target format.")

if __name__ == "__main__":
    main()