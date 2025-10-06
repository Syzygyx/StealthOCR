#!/usr/bin/env python3
"""
View Excel results from PDF to Excel transformation
"""

import pandas as pd
import sys

def view_excel_file(excel_path):
    """View the contents of an Excel file"""
    print(f"📊 Viewing Excel file: {excel_path}")
    print("=" * 60)
    
    try:
        # Read all sheets
        excel_data = pd.read_excel(excel_path, sheet_name=None)
        
        for sheet_name, df in excel_data.items():
            print(f"\n📋 Sheet: {sheet_name}")
            print("-" * 40)
            print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
            print()
            
            # Display the data
            if not df.empty:
                print(df.to_string(index=False, max_cols=4))
            else:
                print("(Empty sheet)")
            print()
            
    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python view_excel_results.py <excel_file>")
        print("Example: python view_excel_results.py test_output_validation.xlsx")
        return
    
    excel_file = sys.argv[1]
    view_excel_file(excel_file)

if __name__ == "__main__":
    main()