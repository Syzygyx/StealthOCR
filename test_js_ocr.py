#!/usr/bin/env python3
"""
Test JavaScript OCR functionality on GitHub Pages
"""

import asyncio
from playwright.async_api import async_playwright

async def test_js_ocr():
    """Test JavaScript OCR with real PDF processing"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Check if upload section is visible
            upload_section = page.locator("#uploadSection")
            await upload_section.wait_for(state="visible", timeout=10000)
            print("✅ Upload section is visible")
            
            # Set up file upload
            pdf_path = "/Users/danielmcshan/Downloads/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf"
            
            # Set up file input
            file_input = page.locator("#fileInput")
            await file_input.set_input_files(pdf_path)
            print(f"📄 Uploaded PDF: {pdf_path}")
            
            # Wait for processing to start
            processing_section = page.locator("#processingSection")
            try:
                await processing_section.wait_for(state="visible", timeout=5000)
                print("✅ Processing section appeared")
            except:
                print("⚠️ Processing section didn't appear immediately")
            
            # Wait for results (this might take a while for OCR)
            print("⏳ Waiting for JavaScript OCR to complete...")
            results_layout = page.locator("#resultsLayout")
            
            # Wait up to 2 minutes for OCR to complete
            try:
                await results_layout.wait_for(state="visible", timeout=120000)
                print("✅ Results layout is visible (OCR completed)")
                
                # Check if CSV container has content
                csv_container = page.locator("#excelContainer")
                if await csv_container.is_visible():
                    print("✅ CSV container is visible")
                    
                    # Check if CSV table is present
                    csv_table = csv_container.locator("table.csv-table")
                    if await csv_table.count() > 0:
                        print("✅ CSV table is present")
                        
                        # Get table data
                        rows = await csv_table.locator("tr").count()
                        print(f"📊 CSV table has {rows} rows")
                        
                        # Check if it's real OCR data (not demo)
                        first_row = csv_table.locator("tr").nth(1)
                        if first_row:
                            cells = await first_row.locator("td").all_text_contents()
                            if "DEMO MODE" in str(cells):
                                print("⚠️ Still showing demo mode data")
                            else:
                                print("✅ Real OCR data detected")
                                
                                # Print first few rows of data
                                for i in range(min(3, rows)):
                                    row = csv_table.locator("tr").nth(i)
                                    if await row.is_visible():
                                        row_text = await row.text_content()
                                        print(f"   Row {i}: {row_text[:100]}...")
                    else:
                        print("❌ CSV table not found")
                else:
                    print("❌ CSV container not visible")
                
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
                
                print("🎉 JavaScript OCR test completed successfully!")
                
            except Exception as e:
                print(f"❌ Results layout not visible: {e}")
                
                # Check if there are any error messages
                message_container = page.locator("#messageContainer")
                if await message_container.is_visible():
                    error_message = await message_container.text_content()
                    print(f"📝 Error message: {error_message}")
                
                # Check console for errors
                console_messages = []
                page.on("console", lambda msg: console_messages.append(msg.text) if msg.type == "error" else None)
                
                if console_messages:
                    print("📝 Console errors:")
                    for msg in console_messages:
                        print(f"   {msg}")
            
            # Take a screenshot for debugging
            await page.screenshot(path="js_ocr_test_result.png")
            print("📸 Screenshot saved as js_ocr_test_result.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="js_ocr_test_error.png")
            print("📸 Error screenshot saved as js_ocr_test_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_js_ocr())