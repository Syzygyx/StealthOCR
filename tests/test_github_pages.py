"""
Playwright tests for StealthOCR on GitHub Pages
"""

import pytest
import os
import time
from playwright.sync_api import Page, expect

class TestStealthOCRGitHubPages:
    """Tests for StealthOCR deployed on GitHub Pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Setup for each test"""
        # Use GitHub Pages URL
        self.github_pages_url = "https://syzygyx.github.io/StealthOCR"
        page.goto(self.github_pages_url)
        page.wait_for_load_state("networkidle")
    
    def test_github_pages_loads(self, page: Page):
        """Test that GitHub Pages loads correctly"""
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
    
    def test_ui_elements_present(self, page: Page):
        """Test that all UI elements are present"""
        # Check file input
        file_input = page.locator("#fileInput")
        expect(file_input).to_be_visible()
        expect(file_input).to_have_attribute("accept", ".pdf")
        
        # Check upload button
        upload_btn = page.locator("button:has-text('Choose PDF File')")
        expect(upload_btn).to_be_visible()
        
        # Check file info section (initially hidden)
        file_info = page.locator("#fileInfo")
        expect(file_info).not_to_be_visible()
        
        # Check processing section (initially hidden)
        processing_section = page.locator("#processingSection")
        expect(processing_section).not_to_be_visible()
        
        # Check results section (initially hidden)
        results_section = page.locator("#resultsSection")
        expect(results_section).not_to_be_visible()
    
    def test_file_validation_github_pages(self, page: Page):
        """Test file type validation on GitHub Pages"""
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
    def test_pdf_upload_flow_github_pages(self, page: Page):
        """Test PDF upload flow on GitHub Pages with actual PDF"""
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
        
        # Wait for results (with longer timeout for GitHub Pages)
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=120000)  # 2 minutes
            
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
            
            print(f"✅ GitHub Pages: Successfully extracted {len(extracted_text)} characters")
            print(f"✅ GitHub Pages: Found {len(found_content)} expected content samples: {found_content}")
            
        except Exception as e:
            # Check for error message
            error_msg = page.locator(".error-message")
            if error_msg.is_visible():
                print(f"❌ GitHub Pages processing failed: {error_msg.text_content()}")
            else:
                print(f"❌ GitHub Pages processing timed out or failed: {e}")
            raise e
    
    def test_responsive_design_github_pages(self, page: Page):
        """Test responsive design on GitHub Pages"""
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
    
    def test_api_configuration_github_pages(self, page: Page):
        """Test that API configuration is correct for GitHub Pages"""
        # Check that the page loads without JavaScript errors
        # This indirectly tests that the config.js is loaded correctly
        
        # Check for any JavaScript errors in console
        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg.text))
        
        # Reload page to capture any console errors
        page.reload()
        page.wait_for_load_state("networkidle")
        
        # Check for critical errors (ignore warnings)
        error_logs = [log for log in console_logs if "error" in log.lower() and "cors" not in log.lower()]
        
        # Should not have critical JavaScript errors
        assert len(error_logs) == 0, f"JavaScript errors found: {error_logs}"
    
    def test_download_functionality_github_pages(self, page: Page):
        """Test download functionality on GitHub Pages"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Wait for results
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=120000)
            
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
            
            print(f"✅ GitHub Pages: Download functionality works correctly")
            
            # Clean up
            os.remove(download_path)
            
        except Exception as e:
            print(f"❌ GitHub Pages download test failed: {e}")
            raise e
    
    def test_error_handling_github_pages(self, page: Page):
        """Test error handling on GitHub Pages"""
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
    
    def test_statistics_display_github_pages(self, page: Page):
        """Test that statistics are displayed correctly on GitHub Pages"""
        pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
        
        if not os.path.exists(pdf_path):
            pytest.skip("Test PDF file not found")
        
        # Upload PDF
        page.set_input_files("#fileInput", pdf_path)
        
        # Wait for results
        try:
            expect(page.locator("#resultsSection")).to_be_visible(timeout=120000)
            
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
            
            print("✅ GitHub Pages: Statistics display correctly")
            
        except Exception as e:
            print(f"❌ GitHub Pages statistics test failed: {e}")
            raise e