#!/usr/bin/env python3
"""
Debug the PDF loading issue
"""

import asyncio
from playwright.async_api import async_playwright

async def debug_simple():
    """Debug PDF loading"""
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=2000)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track console messages
        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))
        
        try:
            print("🌐 Loading GitHub Pages...")
            await page.goto("https://syzygyx.github.io/StealthOCR/")
            await page.wait_for_load_state("networkidle")
            
            print("✅ Page loaded successfully")
            
            # Wait a bit
            print("⏳ Waiting 10 seconds...")
            await page.wait_for_timeout(10000)
            
            # Print console messages
            print("\n📝 Console Messages:")
            for msg in console_messages:
                print(f"  {msg}")
            
            # Check if PDF.js loaded
            pdf_js_loaded = await page.evaluate("typeof pdfjsLib !== 'undefined'")
            print(f"\n📚 PDF.js loaded: {pdf_js_loaded}")
            
            # Try to load PDF manually
            print("\n🔍 Testing PDF loading manually...")
            try:
                result = await page.evaluate("""
                    async () => {
                        try {
                            const pdf = await pdfjsLib.getDocument('/25-08_IR_Israel_Security_Replacement_Transfer_Fund_Tranche_3.pdf').promise;
                            return { success: true, pages: pdf.numPages };
                        } catch (error) {
                            return { success: false, error: error.message };
                        }
                    }
                """)
                print(f"📄 PDF load result: {result}")
            except Exception as e:
                print(f"❌ Error testing PDF: {e}")
            
            # Take a screenshot
            await page.screenshot(path="debug_simple.png")
            print("\n📸 Screenshot saved as debug_simple.png")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_simple())