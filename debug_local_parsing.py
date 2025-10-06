#!/usr/bin/env python3
"""
Debug the local parsing issue
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_local_parsing():
    """Debug local parsing"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Capture all console messages
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        
        try:
            print("🌐 Loading local server...")
            await page.goto("http://localhost:8080")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Check what elements are visible
            upload_section = page.locator("#uploadSection")
            results_layout = page.locator("#resultsLayout")
            csv_section = page.locator("#csvSection")
            csv_table = page.locator("#csvTable")
            
            print(f"Upload section visible: {await upload_section.is_visible()}")
            print(f"Results layout visible: {await results_layout.is_visible()}")
            print(f"CSV section visible: {await csv_section.is_visible()}")
            print(f"CSV table visible: {await csv_table.is_visible()}")
            
            # Wait for processing
            print("⏳ Waiting 20 seconds for processing...")
            await page.wait_for_timeout(20000)
            
            # Check again after waiting
            print(f"After wait - Upload section visible: {await upload_section.is_visible()}")
            print(f"After wait - Results layout visible: {await results_layout.is_visible()}")
            print(f"After wait - CSV section visible: {await csv_section.is_visible()}")
            print(f"After wait - CSV table visible: {await csv_table.is_visible()}")
            
            # Check if there's any content in the CSV section
            csv_content = await page.text_content("#csvSection")
            print(f"\nCSV section content: {csv_content}")
            
            # Check for any error messages
            error_elements = page.locator(".error, .error-message")
            if await error_elements.count() > 0:
                print(f"Found {await error_elements.count()} error elements")
                for i in range(await error_elements.count()):
                    error_text = await error_elements.nth(i).text_content()
                    print(f"Error {i}: {error_text}")
            
            print(f"\n📝 All console logs ({len(console_logs)} total):")
            for i, log in enumerate(console_logs):
                print(f"  {i+1}: {log}")
            
            # Take a screenshot
            await page.screenshot(path="debug_local_parsing.png")
            print("\n📸 Screenshot saved as debug_local_parsing.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_local_parsing())