import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrape_detail_page(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set to False if you want to see it
        page = await browser.new_page()

        try:
            # Step 1: Go to search page
            await page.goto("https://pdki-indonesia.dgip.go.id/search", wait_until="networkidle")
            print("Opened search page")

            # DEBUG: List all input elements
            inputs = await page.query_selector_all("input")
            print(f"🔍 Found {len(inputs)} <input> elements")

            for i, input_element in enumerate(inputs):
                attr = await input_element.get_attribute("class")
                placeholder = await input_element.get_attribute("placeholder")
                value = await input_element.get_attribute("value")
                print(f"Input #{i+1} => class: {attr}, placeholder: {placeholder}, value: {value}")

            # Step 2: Fill the keyword into the input
            await page.wait_for_selector('input[role="textbox"]', timeout=10000)
            await page.fill('input[role="textbox"]', keyword)
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            print("Submitted search")

            # Step 3: Wait for the first search result to appear
            await page.wait_for_selector('a[href^="/link/"]', timeout=15000)
            print("Search result appeared")

            # Optional: Take screenshot of result page
            await page.screenshot(path="search_result_page.png", full_page=True)

            # Step 4: Click the first result
            await page.click('a[href^="/link/"]')
            print("Clicked first result")

            # Step 5: Wait until the detail page loads
            await page.wait_for_selector("text=Kode kelas", timeout=10000)

            # Step 6: Scrape HTML
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Save to file
            with open("scraped_detail_page.html", "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))

            # Screenshot of detail page
            await page.screenshot(path="scraped_detail_page.png", full_page=True)

            print("✅ Detail page scraped successfully!")

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

# Run it
async def main():
    keyword = "D001999003660"  # Change this to anything you want to search
    await scrape_detail_page(keyword)

if __name__ == '__main__':
    asyncio.run(main())
