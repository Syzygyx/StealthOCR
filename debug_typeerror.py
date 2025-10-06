#!/usr/bin/env python3
"""
Debug TypeError in GitHub Pages
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_typeerror():
    """Debug the TypeError issue"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            # Listen for console errors
            console_errors = []
            
            def handle_console(msg):
                if msg.type == "error":
                    console_errors.append(msg.text)
                    print(f"❌ Console Error: {msg.text}")
            
            page.on("console", handle_console)
            
            # Listen for page errors
            page_errors = []
            
            def handle_page_error(error):
                page_errors.append(str(error))
                print(f"❌ Page Error: {error}")
            
            page.on("pageerror", handle_page_error)
            
            print("✅ Page loaded, checking for errors...")
            await page.wait_for_timeout(3000)
            
            # Check if there are any JavaScript errors
            if console_errors:
                print(f"\n📋 Found {len(console_errors)} console errors:")
                for i, error in enumerate(console_errors, 1):
                    print(f"  {i}. {error}")
            
            if page_errors:
                print(f"\n📋 Found {len(page_errors)} page errors:")
                for i, error in enumerate(page_errors, 1):
                    print(f"  {i}. {error}")
            
            # Check if the page is working
            upload_section = page.locator("#uploadSection")
            if await upload_section.is_visible():
                print("✅ Upload section is visible")
            else:
                print("❌ Upload section not visible")
            
            # Try to click upload section
            try:
                await upload_section.click()
                print("✅ Upload section clicked successfully")
                await page.wait_for_timeout(2000)
            except Exception as e:
                print(f"❌ Error clicking upload section: {e}")
            
            # Check if results layout appears
            results_layout = page.locator("#resultsLayout")
            if await results_layout.is_visible():
                print("✅ Results layout is visible")
            else:
                print("❌ Results layout not visible")
            
            # Take a screenshot
            await page.screenshot(path="debug_screenshot.png")
            print("📸 Screenshot saved as debug_screenshot.png")
            
        except Exception as e:
            print(f"❌ Debug failed with error: {e}")
            await page.screenshot(path="debug_error.png")
            print("📸 Error screenshot saved as debug_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_typeerror())