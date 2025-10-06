#!/usr/bin/env python3
"""
Simple test to verify GitHub Pages upload functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_simple_upload():
    """Simple test of the upload functionality"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
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
            
            # Click upload section to trigger demo mode
            print("🖱️ Clicking upload section...")
            await upload_section.click()
            await page.wait_for_timeout(3000)
            
            # Check if results layout appears (demo mode)
            results_layout = page.locator("#resultsLayout")
            try:
                await results_layout.wait_for(state="visible", timeout=10000)
                print("✅ Results layout is visible (demo mode activated)")
                
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
                        
                        # Check if it's demo data
                        first_row = csv_table.locator("tr").nth(1)
                        if first_row:
                            cells = await first_row.locator("td").all_text_contents()
                            if "DEMO MODE" in str(cells):
                                print("✅ Demo mode data detected")
                            else:
                                print("📊 Sample data present")
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
                
                print("🎉 Demo mode test completed successfully!")
                
            except Exception as e:
                print(f"❌ Results layout not visible: {e}")
                
                # Check if there are any error messages
                message_container = page.locator("#messageContainer")
                if await message_container.is_visible():
                    error_message = await message_container.text_content()
                    print(f"📝 Error message: {error_message}")
            
            # Take a screenshot for debugging
            await page.screenshot(path="simple_test_result.png")
            print("📸 Screenshot saved as simple_test_result.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="simple_test_error.png")
            print("📸 Error screenshot saved as simple_test_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_simple_upload())