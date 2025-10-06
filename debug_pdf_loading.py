#!/usr/bin/env python3
"""
Debug PDF loading issue
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_pdf_loading():
    """Debug why PDF isn't loading"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track console messages and network requests
        console_messages = []
        network_requests = []
        
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        page.on("request", lambda req: network_requests.append(f"REQUEST: {req.method} {req.url}"))
        page.on("response", lambda resp: network_requests.append(f"RESPONSE: {resp.status} {resp.url}"))
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Wait for PDF loading
            print("⏳ Waiting 10 seconds for PDF loading...")
            await page.wait_for_timeout(10000)
            
            # Print console messages
            print("\n📝 Console Messages:")
            for msg in console_messages:
                print(f"  {msg}")
            
            # Print network requests
            print("\n🌐 Network Requests:")
            for req in network_requests:
                print(f"  {req}")
            
            # Check if PDF was fetched
            pdf_requests = [req for req in network_requests if "25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf" in req]
            if pdf_requests:
                print(f"\n📄 PDF requests found: {len(pdf_requests)}")
                for req in pdf_requests:
                    print(f"  {req}")
            else:
                print("\n❌ No PDF requests found")
            
            # Check CSV content
            csv_container = page.locator("#excelContainer")
            content = await csv_container.text_content()
            print(f"\n📊 CSV content: {content}")
            
            # Take a screenshot
            await page.screenshot(path="debug_pdf_loading.png")
            print("\n📸 Screenshot saved as debug_pdf_loading.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            await page.screenshot(path="debug_pdf_loading_error.png")
            print("📸 Error screenshot saved as debug_pdf_loading_error.png")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_pdf_loading())