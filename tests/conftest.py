"""
Pytest configuration and fixtures for StealthOCR tests
"""

import pytest
import subprocess
import time
import os
import signal
import threading
from playwright.sync_api import sync_playwright
import json
import base64

# Test server configuration
TEST_SERVER_PORT = 8000
TEST_SERVER_URL = f"http://localhost:{TEST_SERVER_PORT}"

class MockOCRServer:
    """Mock OCR server for testing"""
    
    def __init__(self):
        self.server_process = None
        self.mock_results = {
            "success": True,
            "text": self._get_expected_text(),
            "engine": "tesseract",
            "pages_processed": 3,
            "character_count": 5730,
            "word_count": 807,
            "line_count": 156
        }
    
    def _get_expected_text(self):
        """Return expected text from the test PDF"""
        return """=== PAGE 1 ===
Unclassified REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Israel Security Replacement Transfer Fund Tranche 3 DoD Serial Number:

Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?
Yes

Component Serial Number: (Amounts in Thousands of Dollars)
Program Base Reflecting Program Previously Reprogramming Action Revised Program
Congressional Action Approved by Sec Def

This reprogramming action provides funding for the replacement of defense articles from the stocks of the
Department of Defense expended in support of Israel and for the reimbursement of defense services of the
Department of Defense provided to Israel or identified and notified to Congress for provision to Israel. This
action is determined to be necessary in the national interest. This reprogramming action meets all
administrative and legal requirements, and none of the items have been previously denied by the Congress.

This reprogramming action transfers $657.

=== PAGE 2 ===
[Additional content from page 2...]

=== PAGE 3 ===
[Additional content from page 3...]"""
    
    def start(self):
        """Start the mock server"""
        # Create a simple HTTP server that mocks the OCR API
        server_code = '''
import http.server
import socketserver
import json
import base64
from urllib.parse import urlparse, parse_qs

class MockOCRHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/ocr':
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                # Mock response
                response = {
                    "success": True,
                    "text": """=== PAGE 1 ===
Unclassified REPROGRAMMING ACTION - INTERNAL REPROGRAMMING

Subject: Israel Security Replacement Transfer Fund Tranche 3 DoD Serial Number:

Appropriation Title: Various Appropriations FY 25-08 IR

Includes Transfer?
Yes

Component Serial Number: (Amounts in Thousands of Dollars)
Program Base Reflecting Program Previously Reprogramming Action Revised Program
Congressional Action Approved by Sec Def

This reprogramming action provides funding for the replacement of defense articles from the stocks of the
Department of Defense expended in support of Israel and for the reimbursement of defense services of the
Department of Defense provided to Israel or identified and notified to Congress for provision to Israel. This
action is determined to be necessary in the national interest. This reprogramming action meets all
administrative and legal requirements, and none of the items have been previously denied by the Congress.

This reprogramming action transfers $657.

=== PAGE 2 ===
[Additional content from page 2...]

=== PAGE 3 ===
[Additional content from page 3...]""",
                    "engine": "tesseract",
                    "pages_processed": 3,
                    "character_count": 5730,
                    "word_count": 807,
                    "line_count": 156
                }
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                # Send error response
                error_response = {
                    "success": False,
                    "error": str(e)
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", 8000), MockOCRHandler) as httpd:
        print("Mock OCR server running on port 8000...")
        httpd.serve_forever()
'''
        
        # Write server code to temporary file
        with open('/tmp/mock_ocr_server.py', 'w') as f:
            f.write(server_code)
        
        # Start the server
        self.server_process = subprocess.Popen([
            'python', '/tmp/mock_ocr_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(2)
    
    def stop(self):
        """Stop the mock server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.wait()
        
        # Clean up temporary file
        if os.path.exists('/tmp/mock_ocr_server.py'):
            os.remove('/tmp/mock_ocr_server.py')

@pytest.fixture(scope="session")
def mock_server():
    """Fixture for mock OCR server"""
    server = MockOCRServer()
    server.start()
    yield server
    server.stop()

@pytest.fixture(scope="session")
def browser_context_args():
    """Browser context arguments"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True
    }

@pytest.fixture
def page(mock_server, browser_context_args):
    """Page fixture with mock server"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(**browser_context_args)
        page = context.new_page()
        
        # Mock the API calls to use our mock server
        def handle_route(route):
            if route.request.url.endswith('/api/ocr'):
                # Let the mock server handle this
                route.continue_()
            else:
                route.continue_()
        
        page.route("**/*", handle_route)
        
        yield page
        
        context.close()
        browser.close()

@pytest.fixture
def test_pdf_path():
    """Path to test PDF file"""
    return "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"

@pytest.fixture
def expected_text_samples():
    """Expected text samples from the test PDF"""
    return [
        "REPROGRAMMING ACTION",
        "Israel Security Replacement Transfer Fund",
        "Tranche 3",
        "DoD Serial Number",
        "Appropriation Title",
        "Various Appropriations FY 25-08 IR",
        "Component Serial Number",
        "Amounts in Thousands of Dollars",
        "Program Base",
        "Congressional Action",
        "reprogramming action provides funding",
        "replacement of defense articles",
        "Department of Defense",
        "support of Israel",
        "reimbursement of defense services",
        "national interest",
        "administrative and legal requirements",
        "transfers $657"
    ]