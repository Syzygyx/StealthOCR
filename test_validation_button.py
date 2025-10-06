#!/usr/bin/env python3
"""
Test the Run Example Test button functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_validation_button():
    """Test the Run Example Test button with actual PDF processing"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Check if validation button is visible
            validation_btn = page.locator("#runExampleBtn")
            await validation_btn.wait_for(state="visible", timeout=10000)
            print("✅ Validation button is visible")
            
            # Check button text
            button_text = await validation_btn.text_content()
            print(f"📝 Button text: '{button_text}'")
            
            # Click the validation button
            print("🖱️ Clicking Run Example Test button...")
            await validation_btn.click()
            
            # Wait for file dialog to appear (this will timeout, which is expected)
            print("⏳ Waiting for file dialog...")
            try:
                # This will timeout because we can't interact with file dialogs in headless mode
                await page.wait_for_timeout(5000)
                print("✅ File dialog should have appeared")
            except:
                print("⚠️ File dialog interaction not possible in automated mode")
            
            # Check if validation results panel appeared
            validation_results = page.locator("#validationResults")
            try:
                await validation_results.wait_for(state="visible", timeout=5000)
                print("✅ Validation results panel is visible")
                
                # Check validation status
                validation_status = page.locator("#validationStatus")
                if await validation_status.is_visible():
                    status_text = await validation_status.text_content()
                    print(f"📊 Validation status: {status_text}")
                else:
                    print("❌ Validation status not visible")
                
                # Check validation details
                validation_details = page.locator("#validationDetails")
                if await validation_details.is_visible():
                    details_text = await validation_details.text_content()
                    print(f"📋 Validation details: {details_text[:200]}...")
                else:
                    print("❌ Validation details not visible")
                    
            except:
                print("❌ Validation results panel not visible")
            
            # Test the layout
            print("\n🔍 Checking layout structure...")
            
            # Check upload layout
            upload_layout = page.locator(".upload-layout")
            if await upload_layout.is_visible():
                print("✅ Upload layout is visible")
                
                # Check PDF column
                pdf_column = page.locator(".pdf-column")
                if await pdf_column.is_visible():
                    print("✅ PDF column is visible")
                else:
                    print("❌ PDF column not visible")
                
                # Check instructions column
                instructions_column = page.locator(".instructions-column")
                if await instructions_column.is_visible():
                    print("✅ Instructions column is visible")
                else:
                    print("❌ Instructions column not visible")
            
            # Check footer
            footer = page.locator(".footer")
            if await footer.is_visible():
                print("✅ Footer is visible")
                
                datetime_display = page.locator("#currentDateTime")
                if await datetime_display.is_visible():
                    datetime_text = await datetime_display.text_content()
                    print(f"🕒 Date/time: {datetime_text}")
                else:
                    print("❌ Date/time display not visible")
            else:
                print("❌ Footer not visible")
            
            # Take a screenshot
            await page.screenshot(path="validation_button_test_result.png")
            print("📸 Screenshot saved as validation_button_test_result.png")
            
            print("\n🎉 Validation button test completed!")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="validation_button_test_error.png")
            print("📸 Error screenshot saved as validation_button_test_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_validation_button())