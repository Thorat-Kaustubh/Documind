import os
import asyncio
import json
import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import logging
from typing import Dict, Any, Optional
from backend.src.execution.llm_engine import LLMEngine

logger = logging.getLogger("documind.screener")

class ScreenerAgent:
    """
    ELITE HYBRID SCRAPER: HTTPX + PLAYWRIGHT
    - Hyper-Speed Layer: Try raw HTTPX + BeautifulSoup first (Sub-1s).
    - Precision Fallback: Use Playwright (Sub-8s) if blocked.
    - Zero-Emoji & Minimal Prompt logic for <50ms Token-to-First-Token (TTFT).
    """
    def __init__(self):
        self.llm_engine = LLMEngine()
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"}

    async def get_full_financials(self, ticker: str) -> Dict[str, Any]:
        """Sonic extraction involving a Fast Path (Httpx) and a Safe Path (Playwright)."""
        url = f"https://www.screener.in/company/{ticker}/"
        
        # --- PHASE 1: FAST PATH (Sub-1s) ---
        logger.info(f"Fast-Path attempting direct fetch for {ticker}")
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=5.0) as client:
                response = await client.get(url, follow_redirects=True)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    # Check for core financial sections
                    if soup.select("#profit-loss"):
                        logger.info(f"Fast-Path hit: Extracting DOM for {ticker}")
                        # Extract the inner text of core sections only
                        content = ""
                        for sel in ["#profit-loss", "#balance-sheet", "#cash-flow", "#quarters"]:
                            element = soup.select_one(sel)
                            if element:
                                content += f"\n\n--- {sel} ---\n{element.get_text(separator=' ', strip=True)}"
                        
                        return await self.llm_engine.generate_response(
                            task=f"Extract fundamental metrics and financial health summary for {ticker}.",
                            context=content,
                            mode="fast"
                        )
        except Exception as e:
            logger.debug(f"Fast-Path blocked or error: {str(e)[:40]}")

        # --- PHASE 2: FALLBACK PATH (Sub-8s) ---
        logger.info(f"Safe-Path fallback (Playwright) for {ticker}")
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Resource Blocking for speed
            async def block_resources(route):
                if route.request.resource_type in ["image", "font", "media", "stylesheet"]:
                    await route.abort()
                else:
                    await route.continue_()
            await page.route("**/*", block_resources)
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                combined_html = await page.evaluate("""() => {
                    const sections = ["#profit-loss", "#balance-sheet", "#cash-flow", "#quarters"];
                    let results = "";
                    sections.forEach(sel => {
                        const el = document.querySelector(sel);
                        if (el) { el.querySelectorAll('script, style, a').forEach(s => s.remove()); results += `\\n\\n--- ${sel} ---\\n` + el.innerText; }
                    });
                    return results;
                }""")
                await browser.close()
                return await self.llm_engine.generate_response(
                    task=f"Extract fundamental metrics and financial health summary for {ticker}.",
                    context=combined_html,
                    mode="fast"
                )
            except Exception as e:
                await browser.close()
                return {"status": "FAILED", "reason": str(e)}
