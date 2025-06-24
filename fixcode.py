import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_with_playwright(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Set headless=False to see the browser
        page = await browser.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle') # wait_until='networkidle' is similar to 'networkidle0'

            await page.wait_for_selector('h3:has-text("Alamat Kantor")', timeout=20000) # Wait til "Alamat Kantor" text appears
            
            # Add small delay to avoid blocking by browser
            await asyncio.sleep(2) 

            # Get the full HTML
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Save to txt file
            with open('scraped_page.txt', 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print("Data saved")

            # Take a screenshot to track progress
            await page.screenshot(path='scraped_page.png', full_page=True)
            print("Screenshoted")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

async def main_playwright():
    url = "https://pdki-indonesia.dgip.go.id/search"
    await scrape_with_playwright(url)

if __name__ == '__main__':
    asyncio.run(main_playwright())