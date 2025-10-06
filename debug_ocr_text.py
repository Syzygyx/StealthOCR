#!/usr/bin/env python3
"""
Debug the actual OCR text being extracted
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_ocr_text():
    """Debug the actual OCR text"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Wait for processing
            print("⏳ Waiting 30 seconds for processing...")
            await page.wait_for_timeout(30000)
            
            # Get the extracted text from the browser
            extracted_text = await page.evaluate("""
                () => {
                    return window.extractedText || 'No text found';
                }
            """)
            
            print(f"\n📄 Extracted Text (first 500 chars):")
            print(extracted_text[:500])
            print("...")
            print(f"\n📊 Total length: {len(extracted_text)} characters")
            
            # Check if there are any specific keywords
            keywords = ['REPROGRAMMING', 'ARMY', 'NAVY', 'AIR FORCE', '118,600', '105,252']
            found_keywords = [kw for kw in keywords if kw in extracted_text.upper()]
            print(f"\n🔍 Found keywords: {found_keywords}")
            
            # Take a screenshot
            await page.screenshot(path="debug_ocr_text.png")
            print("\n📸 Screenshot saved as debug_ocr_text.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_ocr_text())