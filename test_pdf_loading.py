#!/usr/bin/env python3
"""
Test PDF loading and processing
"""

import asyncio
from playwright.async_api import async_playwright

async def test_pdf_loading():
    """Test if PDF loads and processes correctly"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
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
                return
            
            # Wait for PDF processing
            print("⏳ Waiting 60 seconds for PDF processing...")
            await page.wait_for_timeout(60000)
            
            # Check CSV content
            csv_container = page.locator("#excelContainer")
            content = await csv_container.text_content()
            print(f"📊 CSV content: {content[:200]}...")
            
            # Check if CSV table exists
            csv_table = page.locator("table")
            if await csv_table.count() > 0:
                print("✅ CSV table found")
                rows = await csv_table.locator("tr").count()
                print(f"📊 CSV table has {rows} rows")
                
                # Check first few rows
                for i in range(min(3, rows)):
                    row_text = await csv_table.locator("tr").nth(i).text_content()
                    print(f"  Row {i}: {row_text[:100]}...")
            else:
                print("❌ No CSV table found")
            
            # Check PDF canvas
            pdf_canvas = page.locator("#pdfCanvas")
            if await pdf_canvas.is_visible():
                print("✅ PDF canvas is visible")
            else:
                print("❌ PDF canvas not visible")
            
            # Take a screenshot
            await page.screenshot(path="pdf_loading_test.png")
            print("📸 Screenshot saved as pdf_loading_test.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path="pdf_loading_error.png")
            print("📸 Error screenshot saved as pdf_loading_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_pdf_loading())