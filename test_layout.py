#!/usr/bin/env python3
"""
Test the layout structure of the StealthOCR page
"""

import asyncio
from playwright.async_api import async_playwright

async def test_layout():
    """Test the page layout and structure"""
    
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
            
            # Check for two-column layout
            upload_layout = page.locator(".upload-layout")
            if await upload_layout.is_visible():
                print("✅ Upload layout container is visible")
                
                # Check left column (PDF)
                pdf_column = page.locator(".pdf-column")
                if await pdf_column.is_visible():
                    print("✅ PDF column is visible")
                else:
                    print("❌ PDF column not visible")
                
                # Check right column (instructions)
                instructions_column = page.locator(".instructions-column")
                if await instructions_column.is_visible():
                    print("✅ Instructions column is visible")
                else:
                    print("❌ Instructions column not visible")
                
                # Check if they're side by side
                pdf_column_box = await pdf_column.bounding_box()
                instructions_column_box = await instructions_column.bounding_box()
                
                if pdf_column_box and instructions_column_box:
                    print(f"📊 PDF column position: x={pdf_column_box['x']:.0f}, y={pdf_column_box['y']:.0f}")
                    print(f"📊 Instructions column position: x={instructions_column_box['x']:.0f}, y={instructions_column_box['y']:.0f}")
                    
                    # Check if they're positioned side by side (instructions should be to the right of PDF)
                    if instructions_column_box['x'] > pdf_column_box['x']:
                        print("✅ Columns are positioned side by side")
                    else:
                        print("❌ Columns are not positioned side by side")
                else:
                    print("❌ Could not get column positions")
            else:
                print("❌ Upload layout container not visible")
            
            # Check for date/time footer
            footer = page.locator(".footer")
            if await footer.is_visible():
                print("✅ Footer is visible")
                
                datetime_display = page.locator("#currentDateTime")
                if await datetime_display.is_visible():
                    datetime_text = await datetime_display.text_content()
                    print(f"✅ Date/time display: {datetime_text}")
                else:
                    print("❌ Date/time display not visible")
            else:
                print("❌ Footer not visible")
            
            # Check validation button
            validation_btn = page.locator("#runExampleBtn")
            if await validation_btn.is_visible():
                print("✅ Validation button is visible")
                
                # Click validation button to test
                await validation_btn.click()
                await page.wait_for_timeout(2000)
                
                validation_results = page.locator("#validationResults")
                if await validation_results.is_visible():
                    print("✅ Validation results panel opened")
                else:
                    print("❌ Validation results panel not opened")
            else:
                print("❌ Validation button not visible")
            
            # Take a screenshot
            await page.screenshot(path="layout_test_result.png")
            print("📸 Screenshot saved as layout_test_result.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="layout_test_error.png")
            print("📸 Error screenshot saved as layout_test_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_layout())