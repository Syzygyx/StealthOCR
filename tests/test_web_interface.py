"""
Playwright tests for StealthOCR web interface
"""

import pytest
import os
import time
from playwright.sync_api import Page, expect
import json
import base64

# Test configuration
TEST_PDF_PATH = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
EXPECTED_TEXT_SAMPLES = [
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

class TestStealthOCRWebInterface:
    """Test suite for StealthOCR web interface"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test"""
        # Start local server if needed
        self.base_url = "http://localhost:8000"
        page.goto(self.base_url)
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
    
    def test_page_loads_correctly(self, page: Page):
        """Test that the main page loads with all elements"""
        # Check page title
        expect(page).to_have_title("StealthOCR - PDF Text Extractor")
        
        # Check main heading
        expect(page.locator("h1")).to_contain_text("🔍 StealthOCR")
        
        # Check subtitle
        expect(page.locator("p")).to_contain_text("Extract text from PDF documents")
        
        # Check upload section
        expect(page.locator("#uploadSection")).to_be_visible()
        expect(page.locator(".upload-icon")).to_be_visible()
        expect(page.locator("text=Upload PDF Document")).to_be_visible()
        
        # Check file input
        expect(page.locator("#fileInput")).to_be_visible()
        expect(page.locator("button:has-text('Choose PDF File')")).to_be_visible()
    
    def test_file_upload_ui(self, page: Page):
        """Test file upload interface elements"""
        # Check drag and drop area
        upload_section = page.locator("#uploadSection")
        expect(upload_section).to_be_visible()
        
        # Check file info section (initially hidden)
        file_info = page.locator("#fileInfo")
        expect(file_info).not_to_be_visible()
        
        # Check processing section (initially hidden)
        processing_section = page.locator("#processingSection")
        expect(processing_section).not_to_be_visible()
        
        # Check results section (initially hidden)
        results_section = page.locator("#resultsSection")
        expect(results_section).not_to_be_visible()
    
    def test_invalid_file_type_rejection(self, page: Page):
        """Test that non-PDF files are rejected"""
        # Create a temporary text file
        test_file_path = "/tmp/test.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file")
        
        # Upload the text file
        page.set_input_files("#fileInput", test_file_path)
        
        # Check for error message
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".error-message")).to_contain_text("Please select a PDF file")
        
        # Clean up
        os.remove(test_file_path)
    
    def test_file_size_validation(self, page: Page):
        """Test file size validation"""
        # This test would require creating a large file
        # For now, we'll test the UI behavior
        upload_section = page.locator("#uploadSection")
        expect(upload_section).to_be_visible()
    
    @pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF file not found")
    def test_pdf_upload_and_processing(self, page: Page):
        """Test PDF upload and processing with the provided test file"""
        # Upload the test PDF
        page.set_input_files("#fileInput", TEST_PDF_PATH)
        
        # Check that file info is displayed
        file_info = page.locator("#fileInfo")
        expect(file_info).to_be_visible()
        expect(file_info).to_contain_text("25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf")
        
        # Check file size is displayed
        expect(file_info).to_contain_text("Size:")
        
        # Wait for processing to start
        processing_section = page.locator("#processingSection")
        expect(processing_section).to_be_visible()
        expect(processing_section).to_contain_text("Processing PDF...")
        
        # Wait for processing to complete (with timeout)
        try:
            # Wait for results section to appear
            expect(page.locator("#resultsSection")).to_be_visible(timeout=60000)  # 60 seconds
            
            # Check results header
            results_header = page.locator(".results-header")
            expect(results_header).to_be_visible()
            expect(results_header).to_contain_text("Extraction Results")
            
            # Check download button
            download_btn = page.locator("#downloadBtn")
            expect(download_btn).to_be_visible()
            expect(download_btn).to_contain_text("Download as TXT")
            
            # Check stats are displayed
            stats = page.locator("#stats")
            expect(stats).to_be_visible()
            
            # Check for word count, character count, etc.
            expect(stats).to_contain_text("Words")
            expect(stats).to_contain_text("Characters")
            expect(stats).to_contain_text("Lines")
            
        except Exception as e:
            # If processing takes too long, check for error message
            error_message = page.locator(".error-message")
            if error_message.is_visible():
                print(f"Processing failed with error: {error_message.text_content()}")
            raise e
    
    @pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF file not found")
    def test_extracted_text_content(self, page: Page):
        """Test that extracted text contains expected content"""
        # Upload the test PDF
        page.set_input_files("#fileInput", TEST_PDF_PATH)
        
        # Wait for processing to complete
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=60000)
            
            # Get the extracted text
            text_output = page.locator("#textOutput")
            expect(text_output).to_be_visible()
            
            extracted_text = text_output.text_content()
            
            # Check that text is not empty
            assert len(extracted_text) > 0, "No text was extracted"
            
            # Check for expected content samples
            found_samples = []
            for sample in EXPECTED_TEXT_SAMPLES:
                if sample.lower() in extracted_text.lower():
                    found_samples.append(sample)
            
            # Assert that we found at least some expected content
            assert len(found_samples) > 0, f"Expected content not found. Found samples: {found_samples}"
            
            # Print found samples for debugging
            print(f"Found {len(found_samples)} expected text samples:")
            for sample in found_samples:
                print(f"  - {sample}")
            
            # Check that we have a reasonable amount of text
            assert len(extracted_text) > 1000, f"Extracted text too short: {len(extracted_text)} characters"
            
        except Exception as e:
            print(f"Text extraction test failed: {e}")
            raise e
    
    @pytest.mark.skipif(not os.path.exists(TEST_PDF_PATH), reason="Test PDF file not found")
    def test_download_functionality(self, page: Page):
        """Test download functionality"""
        # Upload the test PDF
        page.set_input_files("#fileInput", TEST_PDF_PATH)
        
        # Wait for processing to complete
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=60000)
            
            # Set up download handler
            with page.expect_download() as download_info:
                page.click("#downloadBtn")
            
            download = download_info.value
            assert download.suggested_filename.endswith("_extracted.txt")
            
            # Save the downloaded file
            download_path = f"/tmp/{download.suggested_filename}"
            download.save_as(download_path)
            
            # Verify the downloaded file contains text
            with open(download_path, 'r', encoding='utf-8') as f:
                downloaded_text = f.read()
            
            assert len(downloaded_text) > 0, "Downloaded file is empty"
            
            # Clean up
            os.remove(download_path)
            
        except Exception as e:
            print(f"Download test failed: {e}")
            raise e
    
    def test_reset_functionality(self, page: Page):
        """Test reset functionality with Escape key"""
        # Upload a file first
        if os.path.exists(TEST_PDF_PATH):
            page.set_input_files("#fileInput", TEST_PDF_PATH)
            
            # Wait a moment for file info to appear
            page.wait_for_timeout(1000)
            
            # Press Escape to reset
            page.keyboard.press("Escape")
            
            # Check that upload section is visible again
            expect(page.locator("#uploadSection")).to_be_visible()
            
            # Check that file info is hidden
            expect(page.locator("#fileInfo")).not_to_be_visible()
    
    def test_responsive_design(self, page: Page):
        """Test responsive design on different screen sizes"""
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Check that elements are still visible
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        
        # Check that elements are still visible
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()
        
        # Test desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Check that elements are still visible
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()
    
    def test_error_handling(self, page: Page):
        """Test error handling scenarios"""
        # Test with invalid file type
        test_file_path = "/tmp/test.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test file")
        
        page.set_input_files("#fileInput", test_file_path)
        
        # Check for error message
        expect(page.locator(".error-message")).to_be_visible()
        
        # Clean up
        os.remove(test_file_path)
    
    def test_ui_interactions(self, page: Page):
        """Test various UI interactions"""
        # Test drag and drop area hover
        upload_section = page.locator("#uploadSection")
        upload_section.hover()
        
        # Test button hover
        upload_btn = page.locator("button:has-text('Choose PDF File')")
        upload_btn.hover()
        
        # Test clicking upload button
        upload_btn.click()
        
        # The file input should be triggered (though we can't easily test the file dialog)
        # This is more of a UI interaction test