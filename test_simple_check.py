#!/usr/bin/env python3
"""
Simple test to check if the site is working
"""

import asyncio
from playwright.async_api import async_playwright

async def test_simple_check():
    """Simple test to check the site"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
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
            
            # Wait a bit for processing
            print("⏳ Waiting 5 seconds...")
            await page.wait_for_timeout(5000)
            
            # Check CSV content
            csv_container = page.locator("#excelContainer")
            content = await csv_container.text_content()
            print(f"📊 CSV content: {content[:100]}...")
            
            # Check for console errors
            console_messages = []
            page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
            
            print("📝 Console messages:")
            for msg in console_messages[-5:]:  # Show last 5 messages
                print(f"  {msg}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_simple_check())