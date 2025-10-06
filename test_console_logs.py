#!/usr/bin/env python3
"""
Test with console logging to see what's happening
"""

import asyncio
from playwright.async_api import async_playwright

async def test_console_logs():
    """Test with console logging to debug the issue"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Listen to console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Wait for any processing to complete
            print("⏳ Waiting 15 seconds for processing...")
            await page.wait_for_timeout(15000)
            
            # Print console messages
            print("\n📝 Console Messages:")
            for msg in console_messages:
                print(f"  {msg}")
            
            # Check if CSV content changed
            csv_container = page.locator("#excelContainer")
            content = await csv_container.text_content()
            print(f"\n📊 CSV container content: {content}")
            
            # Check if PDF canvas has content
            pdf_canvas = page.locator("#pdfCanvas")
            canvas_visible = await pdf_canvas.is_visible()
            print(f"📄 PDF canvas visible: {canvas_visible}")
            
            # Take a screenshot
            await page.screenshot(path="console_test_result.png")
            print("📸 Screenshot saved as console_test_result.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="console_test_error.png")
            print("📸 Error screenshot saved as console_test_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_console_logs())