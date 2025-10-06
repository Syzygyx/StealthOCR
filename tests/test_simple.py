"""
Simple Playwright tests for StealthOCR validation
"""

import pytest
import os
import time
from playwright.sync_api import Page, expect

class TestStealthOCRSimple:
    """Simple validation tests"""
    
    def test_page_loads(self, page: Page):
        """Test that the page loads correctly"""
        page.goto("http://localhost:8000")
        
        # Check basic elements
        expect(page.locator("h1")).to_contain_text("StealthOCR")
        expect(page.locator("#uploadSection")).to_be_visible()
        expect(page.locator("#fileInput")).to_be_visible()
    
    def test_pdf_upload_ui(self, page: Page):
        """Test PDF upload UI elements"""
        page.goto("http://localhost:8000")
        
        # Check upload section
        upload_section = page.locator("#uploadSection")
        expect(upload_section).to_be_visible()
        
        # Check file input
        file_input = page.locator("#fileInput")
        expect(file_input).to_be_visible()
        expect(file_input).to_have_attribute("accept", ".pdf")
        
        # Check upload button
        upload_btn = page.locator("button:has-text('Choose PDF File')")
        expect(upload_btn).to_be_visible()
    
    def test_file_validation(self, page: Page):
        """Test file type validation"""
        page.goto("http://localhost:8000")
        
        # Create a test text file
        test_file = "/tmp/test.txt"
        with open(test_file, "w") as f:
            f.write("This is not a PDF")
        
        # Try to upload text file
        page.set_input_files("#fileInput", test_file)
        
        # Should show error message
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".error-message")).to_contain_text("Please select a PDF file")
        
        # Clean up
        os.remove(test_file)
    
    @pytest.mark.skipif(not os.path.exists("/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"), 
                        reason="Test PDF not found")
    def test_pdf_upload_flow(self, page: Page):
        """Test PDF upload flow with actual PDF"""
        page.goto("http://localhost:8000")
        
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Check file info appears
        file_info = page.locator("#fileInfo")
        expect(file_info).to_be_visible()
        expect(file_info).to_contain_text("25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf")
        
        # Check processing section appears
        processing_section = page.locator("#processingSection")
        expect(processing_section).to_be_visible()
        expect(processing_section).to_contain_text("Processing PDF...")
        
        # Wait for results (with timeout)
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=60000)
            
            # Check results elements
            expect(page.locator(".results-header")).to_be_visible()
            expect(page.locator("#downloadBtn")).to_be_visible()
            expect(page.locator("#stats")).to_be_visible()
            expect(page.locator("#textOutput")).to_be_visible()
            
            # Check that text was extracted
            text_output = page.locator("#textOutput")
            extracted_text = text_output.text_content()
            
            assert len(extracted_text) > 0, "No text was extracted"
            assert len(extracted_text) > 100, f"Text too short: {len(extracted_text)} characters"
            
            # Check for expected content
            expected_content = [
                "REPROGRAMMING ACTION",
                "Israel Security Replacement Transfer Fund",
                "Tranche 3",
                "Department of Defense",
                "support of Israel"
            ]
            
            found_content = []
            for content in expected_content:
                if content.lower() in extracted_text.lower():
                    found_content.append(content)
            
            assert len(found_content) > 0, f"No expected content found. Found: {found_content}"
            
            print(f"✅ Successfully extracted {len(extracted_text)} characters")
            print(f"✅ Found {len(found_content)} expected content samples: {found_content}")
            
        except Exception as e:
            # Check for error message
            error_msg = page.locator(".error-message")
            if error_msg.is_visible():
                print(f"❌ Processing failed: {error_msg.text_content()}")
            else:
                print(f"❌ Processing timed out or failed: {e}")
            raise e