import asyncio
import os
from typing import Dict, Any, List
from playwright.async_api import async_playwright

class RegulatorScout:
    """
    SPECIALIZED AGENT FOR INSTITUTIONAL DISCOVERY (BSE/NSE/SEC)
    Bypasses WAF by simulating a real investigative session.
    """
    def __init__(self):
        self.bse_base = "https://www.bseindia.com"
        self.nse_base = "https://www.nseindia.com"
        self.proxy_server = os.getenv("PROXY_SERVER_URL")

    async def get_all_bse_filings(self, symbol: str, category: str = "Financial Results") -> List[Dict[str, Any]]:
        """
        FULL HARVESTER: Scours ALL pages of BSE announcements for a given symbol.
        Bypasses WAF via session-warming and handles dynamic pagination.
        """
        print(f"🕵️ [RegScout] Running FULL HARVEST on BSE for {symbol} ({category})...")
        
        async with async_playwright() as p:
            launch_opts = {"headless": True}
            if self.proxy_server:
                launch_opts["proxy"] = {"server": self.proxy_server}
                
            browser = await p.chromium.launch(**launch_opts)
            context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
            page = await context.new_page()

            all_filings = []

            try:
                # 1. Warm-up and Setup Filters
                await page.goto(f"{self.bse_base}/corporates/ann.html", wait_until="domcontentloaded", timeout=45000)
                await asyncio.sleep(5) # Give the heavy BSE JS time to hydrate all filters
                
                # Expand Category via multiple selector types (ID or Name)
                if category:
                    try:
                        selector = "#ddlCategory, select[name*='Category']"
                        await page.wait_for_selector(selector, timeout=10000)
                        await page.select_option(selector, label=category)
                    except:
                        print(f"⚠️ [RegScout] Category dropdown not interaction-ready. Proceeding with default Segment.")
                    await asyncio.sleep(2)

                # Set Date Range (Expand to 1 Month by default for 'Full Harvest')
                try:
                    await page.wait_for_selector("#txtFromDt", timeout=5000)
                    await page.click("#txtFromDt")
                    await page.click("td.ui-datepicker-today >> xpath=.. >> td:nth-child(1)") # Set to 1st of month
                except:
                    print(f"⚠️ [RegScout] Date picker interaction failed. Using current date.")
                await asyncio.sleep(1)

                # 2. Precise Security Selection (Required for BSE to register search)
                await page.fill("#scripsearchtxtbx", symbol)
                await asyncio.sleep(1.5) # Wait for suggest dropdown
                try:
                    await page.click(f"li.ui-menu-item >> text={symbol}")
                    print(f"✅ [RegScout] Selected {symbol} from suggestion list.")
                except:
                    print(f"⚠️ [RegScout] Suggestion list not found, attempting raw Enter.")
                    await page.press("#scripsearchtxtbx", "Enter")

                # 3. Submit Search
                await page.click("input#btnSubmit")
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)

                # 4. PAGINATION LOOP: Fetch ALL pages
                current_page = 1
                while True:
                    # Extract ALL links from current page
                    print(f"📄 [RegScout] Harvesting Page {current_page}...")
                    # Selector for PDF links in the announcements table
                    links = await page.query_selector_all("a[href*='.pdf']")
                    for link in links:
                        href = await link.get_attribute("href")
                        title = await link.inner_text()
                        if href and ".pdf" in href:
                             all_filings.append({
                                "title": title.strip(),
                                "url": f"{self.bse_base}{href}" if href.startswith("/") else href,
                                "source": f"BSE_Page_{current_page}"
                            })

                    # CHECK FOR NEXT PAGE
                    next_btn = await page.query_selector("text=Next")
                    if next_btn and await next_btn.is_visible():
                        print(f"➡️ [RegScout] Navigating to Page {current_page + 1}...")
                        await next_btn.click()
                        await asyncio.sleep(3) # Wait for dynamic table update
                        current_page += 1
                    else:
                        print(f"🏁 [RegScout] Harvest complete. Total filings found: {len(all_filings)}")
                        break

                await browser.close()
                return all_filings

            except Exception as e:
                print(f"❌ [RegScout-Error] Full Harvest failed: {e}")
                await browser.close()
                return all_filings # Return what we found so far

    async def get_latest_bse_filings(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Orchestrated Institutional Discovery: Default to Full Harvest mode.
        """
        # We now default to the high-fidelity full harvester
        return await self.get_all_bse_filings(symbol)

if __name__ == "__main__":
    # Test discovery for RELIANCE (500325 is BSE code)
    scout = RegulatorScout()
    async def test():
        results = await scout.get_latest_bse_filings("500325")
        import json
        print(json.dumps(results, indent=2))
    
    asyncio.run(test())
