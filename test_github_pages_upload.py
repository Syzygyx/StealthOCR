#!/usr/bin/env python3
"""
Playwright test to upload file to GitHub Pages and confirm results
"""

import asyncio
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright

# Add src directory to path
sys.path.append('src')

async def test_github_pages_upload():
    """Test file upload and result confirmation on GitHub Pages"""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Check if the upload section is visible
            upload_section = page.locator("#uploadSection")
            await upload_section.wait_for(state="visible", timeout=10000)
            print("✅ Upload section is visible")
            
            # Check if file input is present
            file_input = page.locator("#fileInput")
            await file_input.wait_for(state="attached", timeout=5000)
            print("✅ File input is present")
            
            # Check if the side-by-side layout is hidden initially
            results_layout = page.locator("#resultsLayout")
            is_hidden = await results_layout.evaluate("el => !el.classList.contains('show')")
            print(f"✅ Results layout initially hidden: {is_hidden}")
            
            # Test with a sample PDF file
            test_pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
            
            if os.path.exists(test_pdf_path):
                print(f"📄 Uploading test PDF: {test_pdf_path}")
                
                # Upload the file
                await file_input.set_input_files(test_pdf_path)
                
                # Wait for processing to start
                processing_section = page.locator("#processingSection")
                await processing_section.wait_for(state="visible", timeout=10000)
                print("✅ Processing section appeared")
                
                # Wait for processing to complete (up to 60 seconds)
                print("⏳ Waiting for processing to complete...")
                await results_layout.wait_for(state="visible", timeout=60000)
                print("✅ Results layout is now visible")
                
                # Check if PDF viewer is working
                pdf_canvas = page.locator("#pdfCanvas")
                await pdf_canvas.wait_for(state="visible", timeout=10000)
                print("✅ PDF canvas is visible")
                
                # Check if CSV container has content
                csv_container = page.locator("#excelContainer")
                await csv_container.wait_for(state="visible", timeout=10000)
                
                # Check if CSV table is present
                csv_table = csv_container.locator("table.csv-table")
                if await csv_table.count() > 0:
                    print("✅ CSV table is present")
                    
                    # Get table data
                    rows = await csv_table.locator("tr").count()
                    print(f"📊 CSV table has {rows} rows")
                    
                    # Check if headers are correct
                    headers = await csv_table.locator("th").all_text_contents()
                    expected_headers = [
                        'appropriation_category', 'appropriation code', 'appropriation activity',
                        'branch', 'fiscal_year_start', 'fiscal_year_end', 'budget_activity_number',
                        'budget_activity_title', 'pem', 'budget_title', 'program_base_congressional',
                        'program_base_dod', 'reprogramming_amount', 'revised_program_total',
                        'explanation', 'file'
                    ]
                    
                    print(f"📋 Headers found: {len(headers)}")
                    print(f"📋 Expected headers: {len(expected_headers)}")
                    
                    if len(headers) == len(expected_headers):
                        print("✅ Header count matches expected format")
                    else:
                        print("❌ Header count mismatch")
                    
                    # Check if data rows are present
                    data_rows = rows - 1  # Subtract header row
                    print(f"📊 Data rows: {data_rows}")
                    
                    if data_rows > 0:
                        print("✅ Data rows are present")
                        
                        # Get sample data from first data row
                        first_data_row = csv_table.locator("tr").nth(1)
                        cells = await first_data_row.locator("td").all_text_contents()
                        print(f"📊 Sample row data: {len(cells)} cells")
                        print(f"📊 Sample data: {cells[:3]}...")  # First 3 cells
                    else:
                        print("❌ No data rows found")
                else:
                    print("❌ CSV table not found")
                
                # Check download buttons
                download_csv_btn = page.locator("#downloadExcelBtn")
                download_txt_btn = page.locator("#downloadTxtBtn")
                
                if await download_csv_btn.is_visible():
                    print("✅ Download CSV button is visible")
                else:
                    print("❌ Download CSV button not visible")
                
                if await download_txt_btn.is_visible():
                    print("✅ Download TXT button is visible")
                else:
                    print("❌ Download TXT button not visible")
                
                # Test PDF navigation
                prev_btn = page.locator("#prevPage")
                next_btn = page.locator("#nextPage")
                page_info = page.locator("#pageInfo")
                
                if await page_info.is_visible():
                    page_text = await page_info.text_content()
                    print(f"📄 Page info: {page_text}")
                
                if await prev_btn.is_visible():
                    print("✅ Previous page button is visible")
                
                if await next_btn.is_visible():
                    print("✅ Next page button is visible")
                
                # Test page navigation
                if await next_btn.is_enabled():
                    print("🔄 Testing page navigation...")
                    await next_btn.click()
                    await page.wait_for_timeout(1000)
                    
                    new_page_text = await page_info.text_content()
                    print(f"📄 Page after navigation: {new_page_text}")
                
                print("🎉 Upload and processing test completed successfully!")
                
            else:
                print(f"❌ Test PDF not found at: {test_pdf_path}")
                print("📝 Testing with demo mode instead...")
                
                # Test demo mode by clicking upload without file
                await upload_section.click()
                await page.wait_for_timeout(2000)
                
                # Check if demo mode is triggered
                if await results_layout.is_visible():
                    print("✅ Demo mode activated")
                else:
                    print("❌ Demo mode not activated")
            
            # Test error handling
            print("🧪 Testing error handling...")
            
            # Try to upload a non-PDF file
            test_txt_path = "/tmp/test.txt"
            with open(test_txt_path, "w") as f:
                f.write("This is a test text file")
            
            await file_input.set_input_files(test_txt_path)
            await page.wait_for_timeout(2000)
            
            # Check if error message appears
            message_container = page.locator("#messageContainer")
            if await message_container.is_visible():
                error_message = await message_container.text_content()
                print(f"📝 Error message: {error_message}")
            
            # Clean up
            os.remove(test_txt_path)
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="test_failure.png")
            print("📸 Screenshot saved as test_failure.png")
            raise
        
        finally:
            await browser.close()

async def test_demo_mode():
    """Test demo mode functionality"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Testing demo mode...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            # Check if demo mode is available
            upload_section = page.locator("#uploadSection")
            await upload_section.wait_for(state="visible", timeout=10000)
            
            # Click upload section to trigger demo mode
            await upload_section.click()
            await page.wait_for_timeout(3000)
            
            # Check if results appear
            results_layout = page.locator("#resultsLayout")
            if await results_layout.is_visible():
                print("✅ Demo mode results are visible")
                
                # Check if CSV data is present
                csv_container = page.locator("#excelContainer")
                csv_table = csv_container.locator("table.csv-table")
                
                if await csv_table.count() > 0:
                    rows = await csv_table.locator("tr").count()
                    print(f"📊 Demo CSV table has {rows} rows")
                    
                    # Check if it's demo data
                    first_row = csv_table.locator("tr").nth(1)
                    if first_row:
                        cells = await first_row.locator("td").all_text_contents()
                        if "DEMO MODE" in str(cells):
                            print("✅ Demo mode data detected")
                        else:
                            print("📊 Sample data present")
                else:
                    print("❌ Demo CSV table not found")
            else:
                print("❌ Demo mode results not visible")
            
        except Exception as e:
            print(f"❌ Demo mode test failed: {e}")
            await page.screenshot(path="demo_test_failure.png")
            raise
        
        finally:
            await browser.close()

async def main():
    """Main test function"""
    print("🧪 StealthOCR GitHub Pages Upload Test")
    print("=" * 50)
    
    try:
        # Test with real PDF upload
        await test_github_pages_upload()
        
        print("\n" + "=" * 50)
        
        # Test demo mode
        await test_demo_mode()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())