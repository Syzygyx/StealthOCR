"""
Simplified validation tests for StealthOCR
"""

import pytest
import os
import time
from playwright.sync_api import Page, expect
import json

class TestStealthOCRValidation:
    """Validation tests for StealthOCR using provided PDF"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test"""
        self.base_url = "http://localhost:8000"
        page.goto(self.base_url)
        page.wait_for_load_state("networkidle")
    
    def test_page_structure(self, page: Page):
        """Test basic page structure and elements"""
        # Check title
        expect(page).to_have_title("StealthOCR - PDF Text Extractor")
        
        # Check main elements
        expect(page.locator("h1")).to_contain_text("🔍 StealthOCR")
        expect(page.locator("#uploadSection")).to_be_visible()
        expect(page.locator("#fileInput")).to_be_visible()
        expect(page.locator("button:has-text('Choose PDF File')")).to_be_visible()
    
    def test_pdf_upload_flow(self, page: Page):
        """Test complete PDF upload and processing flow"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Check file info appears
        file_info = page.locator("#fileInfo")
        expect(file_info).to_be_visible()
        expect(file_info).to_contain_text("25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf")
        
        # Check processing starts
        processing_section = page.locator("#processingSection")
        expect(processing_section).to_be_visible()
        expect(processing_section).to_contain_text("Processing PDF...")
        
        # Wait for results (with timeout)
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=30000)
            
            # Check results structure
            expect(page.locator(".results-header")).to_be_visible()
            expect(page.locator("#downloadBtn")).to_be_visible()
            expect(page.locator("#stats")).to_be_visible()
            expect(page.locator("#textOutput")).to_be_visible()
            
        except Exception as e:
            # Check for error message if processing failed
            error_msg = page.locator(".error-message")
            if error_msg.is_visible():
                print(f"Processing failed: {error_msg.text_content()}")
            raise e
    
    def test_extracted_text_validation(self, page: Page):
        """Validate extracted text contains expected content"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Expected text samples
        expected_samples = [
            "REPROGRAMMING ACTION",
            "Israel Security Replacement Transfer Fund",
            "Tranche 3",
            "DoD Serial Number",
            "Appropriation Title",
            "Various Appropriations FY 25-08 IR",
            "reprogramming action provides funding",
            "replacement of defense articles",
            "Department of Defense",
            "support of Israel",
            "national interest",
            "transfers $657"
        ]
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Wait for results
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=30000)
            
            # Get extracted text
            text_output = page.locator("#textOutput")
            expect(text_output).to_be_visible()
            
            extracted_text = text_output.text_content()
            
            # Validate text content
            assert len(extracted_text) > 0, "No text extracted"
            assert len(extracted_text) > 1000, f"Text too short: {len(extracted_text)} chars"
            
            # Check for expected samples
            found_samples = []
            for sample in expected_samples:
                if sample.lower() in extracted_text.lower():
                    found_samples.append(sample)
            
            # Should find at least 5 expected samples
            assert len(found_samples) >= 5, f"Found only {len(found_samples)} expected samples: {found_samples}"
            
            print(f"✅ Found {len(found_samples)} expected text samples:")
            for sample in found_samples:
                print(f"   - {sample}")
            
        except Exception as e:
            print(f"Text validation failed: {e}")
            raise e
    
    def test_statistics_display(self, page: Page):
        """Test that statistics are displayed correctly"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Wait for results
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=30000)
            
            # Check stats section
            stats = page.locator("#stats")
            expect(stats).to_be_visible()
            
            # Check for stat cards
            stat_cards = page.locator(".stat-card")
            expect(stat_cards).to_have_count(4)  # Words, Characters, Lines, Engine
            
            # Check stat labels
            expect(stats).to_contain_text("Words")
            expect(stats).to_contain_text("Characters")
            expect(stats).to_contain_text("Lines")
            expect(stats).to_contain_text("OCR Engine")
            
            # Check stat numbers are displayed
            stat_numbers = page.locator(".stat-number")
            expect(stat_numbers).to_have_count(4)
            
        except Exception as e:
            print(f"Statistics test failed: {e}")
            raise e
    
    def test_download_functionality(self, page: Page):
        """Test download functionality"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Wait for results
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=30000)
            
            # Test download
            with page.expect_download() as download_info:
                page.click("#downloadBtn")
            
            download = download_info.value
            assert download.suggested_filename.endswith("_extracted.txt")
            
            # Save and verify download
            download_path = f"/tmp/{download.suggested_filename}"
            download.save_as(download_path)
            
            with open(download_path, 'r', encoding='utf-8') as f:
                downloaded_text = f.read()
            
            assert len(downloaded_text) > 0, "Downloaded file is empty"
            assert "REPROGRAMMING ACTION" in downloaded_text, "Expected content not in download"
            
            # Clean up
            os.remove(download_path)
            
        except Exception as e:
            print(f"Download test failed: {e}")
            raise e
    
    def test_error_handling(self, page: Page):
        """Test error handling for invalid files"""
        # Test with text file
        test_file = "/tmp/test.txt"
        with open(test_file, "w") as f:
            f.write("This is not a PDF")
        
        page.set_input_files("#fileInput", test_file)
        
        # Should show error message
        expect(page.locator(".error-message")).to_be_visible()
        expect(page.locator(".error-message")).to_contain_text("Please select a PDF file")
        
        # Clean up
        os.remove(test_file)
    
    def test_responsive_design(self, page: Page):
        """Test responsive design"""
        # Test mobile viewport
        page.set_viewport_size({"width": 375, "height": 667})
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()
        
        # Test tablet viewport
        page.set_viewport_size({"width": 768, "height": 1024})
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()
        
        # Test desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        expect(page.locator("h1")).to_be_visible()
        expect(page.locator("#uploadSection")).to_be_visible()