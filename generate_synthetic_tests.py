#!/usr/bin/env python3
"""
Generate synthetic PDF variations to test CSV generation robustness
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.append('src')

from pdf_to_exact_csv_transformer import PDFToExactCSVTransformer

def create_synthetic_ocr_texts():
    """Create various synthetic OCR text variations"""
    
    synthetic_texts = {
        "basic_format": """
=== PAGE 1 ===
REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Test Security Replacement Transfer Fund
DoD Serial Number: TEST-001

Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?
Yes

ARMY INCREASE +50,000
Operation and Maintenance, Army, 25/25
Budget Activity 01: Operating Forces
Explanation: Funds are required for test operations.

NAVY INCREASE +75,000
Weapons Procurement, Navy, 25/27
Budget Activity 02: Other missiles
Explanation: Funds are required for test weapons.

AIR FORCE INCREASE +100,000
Missile Procurement, Air Force, 25/27
Budget Activity 02: Other missiles
Explanation: Funds are required for test missiles.

DEFENSE-WIDE INCREASE +200,000
Procurement, Defense-Wide, 25/27
Budget Activity 01: Major equipment
Explanation: Funds are required for test equipment.

DEFENSE-WIDE DECREASE -425,000
Operation and Maintenance, Defense-Wide, 24/25
Budget Activity 04: Administration
Explanation: Funds available for transfer.
""",

        "minimal_format": """
REPROGRAMMING ACTION

Subject: Minimal Test Document
DoD Serial Number: MIN-001

ARMY INCREASE +25,000
Explanation: Minimal test funding.

NAVY INCREASE +30,000
Explanation: Minimal test funding.
""",

        "complex_format": """
=== PAGE 1 ===
UNCLASSIFIED REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Complex Multi-Branch Security Enhancement Program
DoD Serial Number: COMPLEX-2025-001

Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?
Yes

Component Serial Number: (Amounts in Thousands of Dollars)

ARMY INCREASE +150,000 +150,000
Operation and Maintenance, Army, 25/25
Budget Activity 01: Operating Forces
150,000 150,000
Explanation: Funds are required for enhanced operational capabilities including advanced training, equipment maintenance, and personnel support for critical defense operations.

NAVY INCREASE +200,000 +200,000
Weapons Procurement, Navy, 25/27
Budget Activity 02: Other missiles
200,000 200,000
Explanation: Funds are required for procurement of advanced missile systems and associated support equipment to enhance naval defensive capabilities.

AIR FORCE INCREASE +175,000 +175,000
Missile Procurement, Air Force, 25/27
Budget Activity 02: Other missiles
175,000 175,000
Explanation: Funds are required for acquisition of next-generation air defense missiles and related systems to maintain air superiority.

DEFENSE-WIDE INCREASE +300,000 +300,000
Procurement, Defense-Wide, 25/27
Budget Activity 01: Major equipment
300,000 300,000
Explanation: Funds are required for procurement of major defense equipment including command and control systems, communications equipment, and other critical infrastructure.

DEFENSE-WIDE DECREASE -825,000
Operation and Maintenance, Defense-Wide, 24/25
Budget Activity 04: Administration and Servicewide Activities
-825,000
Explanation: Funds are available from previous appropriations and can be transferred to support the above requirements.
""",

        "edge_case_format": """
REPROGRAMMING ACTION

Subject: Edge Case Testing Document
DoD Serial Number: EDGE-001

ARMY INCREASE +1,234,567
Explanation: Large amount with commas.

NAVY INCREASE +999
Explanation: Small amount.

AIR FORCE INCREASE +0
Explanation: Zero amount test.

DEFENSE-WIDE INCREASE +1
Explanation: Single digit amount.

DEFENSE-WIDE DECREASE -2,000,000
Explanation: Large negative amount.
""",

        "malformed_format": """
REPROGRAMMING ACTION

Subject: Malformed Test Document
DoD Serial Number: MALFORMED-001

ARMY INCREASE +50,000
No explanation provided.

NAVY INCREASE
Missing amount.

AIR FORCE INCREASE +75,000
Explanation: Partial explanation
""",

        "multi_page_format": """
=== PAGE 1 ===
REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Multi-Page Test Document
DoD Serial Number: MULTI-001

Appropriation Title: Various Appropriations FY 25-08 IR

ARMY INCREASE +100,000
Operation and Maintenance, Army, 25/25
Budget Activity 01: Operating Forces
Explanation: First page funding for army operations.

=== PAGE 2 ===
NAVY INCREASE +150,000
Weapons Procurement, Navy, 25/27
Budget Activity 02: Other missiles
Explanation: Second page funding for navy weapons.

AIR FORCE INCREASE +200,000
Missile Procurement, Air Force, 25/27
Budget Activity 02: Other missiles
Explanation: Second page funding for air force missiles.

=== PAGE 3 ===
DEFENSE-WIDE INCREASE +250,000
Procurement, Defense-Wide, 25/27
Budget Activity 01: Major equipment
Explanation: Third page funding for defense-wide procurement.

DEFENSE-WIDE DECREASE -700,000
Operation and Maintenance, Defense-Wide, 24/25
Budget Activity 04: Administration
Explanation: Third page decrease for fund transfer.
"""
    }
    
    return synthetic_texts

def test_synthetic_variations():
    """Test CSV generation with synthetic variations"""
    print("🧪 Testing CSV generation with synthetic variations...")
    print("=" * 60)
    
    transformer = PDFToExactCSVTransformer()
    synthetic_texts = create_synthetic_ocr_texts()
    
    results = {}
    
    for test_name, ocr_text in synthetic_texts.items():
        print(f"\n📋 Testing: {test_name}")
        print("-" * 40)
        
        try:
            # Generate CSV
            output_file = f"synthetic_{test_name}.csv"
            csv_file = transformer.transform_ocr_to_csv(
                ocr_text, 
                output_file,
                f"synthetic_{test_name}.pdf"
            )
            
            # Validate CSV
            import pandas as pd
            df = pd.read_csv(csv_file)
            
            print(f"   ✅ Generated: {len(df)} rows, {len(df.columns)} columns")
            
            # Show sample data
            if not df.empty:
                print(f"   📊 Sample data:")
                for idx, row in df.head(2).iterrows():
                    explanation = str(row['explanation'])[:50] if pd.notna(row['explanation']) else "No explanation"
                    print(f"      Row {idx+1}: {row['branch']} - {row['reprogramming_amount']} - {explanation}...")
            
            results[test_name] = {
                'success': True,
                'rows': len(df),
                'columns': len(df.columns),
                'file': csv_file
            }
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results[test_name] = {
                'success': False,
                'error': str(e)
            }
    
    return results

def validate_all_synthetics():
    """Validate all generated synthetic CSVs"""
    print(f"\n🔍 Validating all synthetic CSVs...")
    print("=" * 60)
    
    synthetic_files = [
        "synthetic_basic_format.csv",
        "synthetic_minimal_format.csv", 
        "synthetic_complex_format.csv",
        "synthetic_edge_case_format.csv",
        "synthetic_malformed_format.csv",
        "synthetic_multi_page_format.csv"
    ]
    
    for csv_file in synthetic_files:
        if os.path.exists(csv_file):
            print(f"\n📄 {csv_file}:")
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                print(f"   Rows: {len(df)}")
                print(f"   Columns: {len(df.columns)}")
                
                if not df.empty:
                    print(f"   Branches: {df['branch'].value_counts().to_dict()}")
                    print(f"   Categories: {df['appropriation_category'].value_counts().to_dict()}")
                    print(f"   Amounts: {df['reprogramming_amount'].tolist()}")
                
            except Exception as e:
                print(f"   ❌ Error reading: {e}")
        else:
            print(f"   ⚠️  File not found: {csv_file}")

def create_stress_test():
    """Create a stress test with many variations"""
    print(f"\n💪 Creating stress test...")
    print("=" * 60)
    
    # Create a large synthetic document
    large_text = """
REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Stress Test Document
DoD Serial Number: STRESS-001

Appropriation Title: Various Appropriations FY 25-08 IR

"""
    
    # Add many appropriation lines
    branches = ['Army', 'Navy', 'Air Force', 'Defense-Wide', 'Marines', 'Coast Guard']
    categories = ['Operation and Maintenance', 'Weapons Procurement', 'Missile Procurement', 'Procurement', 'RDTE']
    
    for i in range(20):
        branch = branches[i % len(branches)]
        category = categories[i % len(categories)]
        amount = (i + 1) * 10000
        
        large_text += f"""
{branch.upper()} INCREASE +{amount:,}
{category}, {branch}, 25/25
Budget Activity {(i % 5) + 1}: Test Activity
Explanation: Stress test funding line {i+1} for {branch} {category} operations.
"""
    
    # Add decrease
    large_text += """
DEFENSE-WIDE DECREASE -500,000
Operation and Maintenance, Defense-Wide, 24/25
Budget Activity 04: Administration
Explanation: Stress test decrease for fund transfer.
"""
    
    # Generate CSV
    transformer = PDFToExactCSVTransformer()
    csv_file = transformer.transform_ocr_to_csv(
        large_text,
        "synthetic_stress_test.csv",
        "synthetic_stress_test.pdf"
    )
    
    print(f"   ✅ Stress test generated: {csv_file}")
    
    # Validate
    import pandas as pd
    df = pd.read_csv(csv_file)
    print(f"   📊 Stress test results: {len(df)} rows, {len(df.columns)} columns")
    
    return csv_file

def main():
    """Main test function"""
    print("🧪 StealthOCR Synthetic Test Generation")
    print("=" * 60)
    
    # Test synthetic variations
    results = test_synthetic_variations()
    
    # Validate all synthetics
    validate_all_synthetics()
    
    # Create stress test
    stress_file = create_stress_test()
    
    # Summary
    print(f"\n📊 Test Summary:")
    print("=" * 60)
    
    successful_tests = sum(1 for r in results.values() if r['success'])
    total_tests = len(results)
    
    print(f"   Successful tests: {successful_tests}/{total_tests}")
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result['success'] else "❌ FAILED"
        if result['success']:
            print(f"   {test_name}: {status} ({result['rows']} rows)")
        else:
            print(f"   {test_name}: {status} ({result['error']})")
    
    print(f"\n📁 Generated files:")
    for result in results.values():
        if result['success']:
            print(f"   - {result['file']}")
    print(f"   - {stress_file}")
    
    return successful_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)