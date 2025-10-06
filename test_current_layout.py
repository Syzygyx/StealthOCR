#!/usr/bin/env python3
"""
Test the current layout to see what's actually displayed
"""

import asyncio
from playwright.async_api import async_playwright

async def test_current_layout():
    """Test what's actually displayed on the current site"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Check if two-column layout exists
            two_column = page.locator("#twoColumnLayout")
            if await two_column.is_visible():
                print("✅ Two-column layout is visible")
            else:
                print("❌ Two-column layout not visible")
            
            # Check PDF viewer section
            pdf_section = page.locator(".pdf-viewer-section")
            if await pdf_section.is_visible():
                print("✅ PDF viewer section is visible")
            else:
                print("❌ PDF viewer section not visible")
            
            # Check CSV section
            csv_section = page.locator(".csv-section")
            if await csv_section.is_visible():
                print("✅ CSV section is visible")
            else:
                print("❌ CSV section not visible")
            
            # Check if PDF canvas exists
            pdf_canvas = page.locator("#pdfCanvas")
            if await pdf_canvas.is_visible():
                print("✅ PDF canvas is visible")
            else:
                print("❌ PDF canvas not visible")
            
            # Check CSV container
            csv_container = page.locator("#excelContainer")
            if await csv_container.is_visible():
                print("✅ CSV container is visible")
                content = await csv_container.text_content()
                print(f"📊 CSV container content: {content[:100]}...")
            else:
                print("❌ CSV container not visible")
            
            # Wait a bit to see if anything loads
            print("⏳ Waiting 10 seconds to see if PDF loads...")
            await page.wait_for_timeout(10000)
            
            # Check again after waiting
            pdf_canvas_after = page.locator("#pdfCanvas")
            if await pdf_canvas_after.is_visible():
                print("✅ PDF canvas visible after waiting")
            else:
                print("❌ PDF canvas still not visible after waiting")
            
            # Take a screenshot
            await page.screenshot(path="current_layout_test.png")
            print("📸 Screenshot saved as current_layout_test.png")
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            await page.screenshot(path="current_layout_error.png")
            print("📸 Error screenshot saved as current_layout_error.png")
            raise
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_current_layout())