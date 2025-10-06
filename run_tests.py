#!/usr/bin/env python3
"""
Test runner for StealthOCR Playwright tests
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

def start_test_server():
    """Start a simple HTTP server for testing"""
    server_process = subprocess.Popen([
        'python', '-m', 'http.server', '8000'
    ], cwd=Path(__file__).parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(2)
    return server_process

def run_playwright_tests():
    """Run Playwright tests"""
    print("🚀 Starting StealthOCR Playwright Tests")
    print("=" * 50)
    
    # Start test server
    print("Starting test server...")
    server_process = start_test_server()
    
    try:
        # Run tests
        print("Running Playwright tests...")
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/test_web_interface.py',
            '--verbose',
            '--browser=chromium',
            '--headed',
            '--video=retain-on-failure',
            '--screenshot=only-on-failure'
        ], capture_output=False)
        
        return result.returncode
        
    finally:
        # Stop test server
        print("Stopping test server...")
        server_process.terminate()
        server_process.wait()

def run_specific_test(test_name):
    """Run a specific test"""
    print(f"🧪 Running test: {test_name}")
    print("=" * 50)
    
    # Start test server
    server_process = start_test_server()
    
    try:
        # Run specific test
        result = subprocess.run([
            'python', '-m', 'pytest', 
            f'tests/test_web_interface.py::{test_name}',
            '--verbose',
            '--browser=chromium',
            '--headed'
        ], capture_output=False)
        
        return result.returncode
        
    finally:
        # Stop test server
        server_process.terminate()
        server_process.wait()

def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        return run_playwright_tests()

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)