#!/usr/bin/env python3
"""
Test runner for StealthOCR on GitHub Pages
"""

import subprocess
import sys
import os
from pathlib import Path

def run_github_pages_tests():
    """Run tests against GitHub Pages deployment"""
    print("🌐 Testing StealthOCR on GitHub Pages")
    print("=" * 50)
    print("URL: https://syzygyx.github.io/StealthOCR")
    print()
    
    # Check if test PDF exists
    test_pdf = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
    if not os.path.exists(test_pdf):
        print("⚠️  Warning: Test PDF not found at expected location")
        print(f"   Expected: {test_pdf}")
        print("   Some tests will be skipped")
        print()
    
    # Run the tests
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/test_github_pages.py',
            '--verbose',
            '--browser=chromium',
            '--headed',
            '--video=retain-on-failure',
            '--screenshot=only-on-failure'
        ], capture_output=False)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"🧪 Running specific test: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            f'tests/test_github_pages.py::{test_name}',
            '--verbose',
            '--browser=chromium',
            '--headed'
        ], capture_output=False)
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return 1

def main():
    """Main test runner"""
    print("StealthOCR GitHub Pages Test Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        return run_github_pages_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)