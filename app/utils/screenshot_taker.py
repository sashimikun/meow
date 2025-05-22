import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def take_screenshot(url: str) -> bytes | None:
    """
    Takes a screenshot of a given URL.

    Args:
        url: The URL to take a screenshot of.

    Returns:
        The screenshot as bytes if successful, None otherwise.
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=30000)  # 30 seconds timeout
            screenshot_bytes = await page.screenshot(full_page=True)
            await browser.close()
            return screenshot_bytes
    except PlaywrightTimeoutError:
        print(f"Timeout error when trying to navigate to {url}")
        return None
    except Exception as e:
        print(f"An error occurred while taking screenshot: {e}")
        return None
