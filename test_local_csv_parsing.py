#!/usr/bin/env python3
"""
Test the local CSV parsing functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_local_csv_parsing():
    """Test CSV parsing on local server"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("🌐 Loading local server...")
            await page.goto("http://localhost:8080")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Wait for PDF processing
            print("⏳ Waiting 30 seconds for PDF processing...")
            await page.wait_for_timeout(30000)
            
            # Check if CSV table is visible
            csv_table = page.locator("#csvTable")
            if await csv_table.is_visible():
                print("✅ CSV table is visible")
                
                # Get the CSV content
                csv_content = await page.text_content("#csvTable")
                print(f"\n📊 CSV Content:")
                print(csv_content[:500] + "..." if len(csv_content) > 500 else csv_content)
                
                # Check for specific data that should be there
                if "Operation and Maintenance" in csv_content:
                    print("✅ Found Army data (Operation and Maintenance)")
                if "Weapons Procurement" in csv_content:
                    print("✅ Found Navy data (Weapons Procurement)")
                if "RDTE" in csv_content:
                    print("✅ Found Air Force data (RDTE)")
                if "118,600" in csv_content:
                    print("✅ Found Army amount (118,600)")
                if "105,252" in csv_content:
                    print("✅ Found Navy amount (105,252)")
                if "30,000" in csv_content:
                    print("✅ Found Air Force amount (30,000)")
                    
            else:
                print("❌ CSV table not visible")
                
            # Check console logs for parsing info
            console_logs = []
            page.on("console", lambda msg: console_logs.append(msg.text))
            
            print(f"\n📝 Console logs:")
            for log in console_logs[-10:]:  # Show last 10 logs
                print(f"  {log}")
            
            # Take a screenshot
            await page.screenshot(path="test_local_csv_parsing.png")
            print("\n📸 Screenshot saved as test_local_csv_parsing.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_local_csv_parsing())