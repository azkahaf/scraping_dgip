import asyncio
from bs4 import BeautifulSoup, Tag
from playwright.async_api import async_playwright

async def scrape_detail_by_keyword(keyword):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Step 1: Open search page
            await page.goto("https://pdki-indonesia.dgip.go.id/search", wait_until="networkidle")
            print("Opened search page")

            # Step 2: Enter keyword and search
            await page.fill("input >> nth=0", keyword)
            await asyncio.sleep(1)
            await page.keyboard.press("Enter")
            print(f"Searching for: {keyword}")

            # Step 3: Click the first result
            await page.wait_for_selector('a[href^="/link/"]', timeout=20000)
            await asyncio.sleep(1)
            await page.click('a[href^="/link/"]')
            print("Clicked the first search result")

            # Step 4: Wait for detail page to load
            await page.wait_for_selector('text=Nomor Registrasi', timeout=20000)
            print("Detail page loaded")

            # Step 5: Scrape HTML content
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Save HTML and Screenshot
            with open("detail_page.html", "w", encoding="utf-8") as f:
                f.write(str(soup.prettify()))
            await page.screenshot(path="detail_page.png", full_page=True)

            class_description = []
            #Parse deskripsi kelas
            # Always iterate over results of find_all
            for tbody in soup.find_all('tbody'):
                if isinstance(tbody, Tag):  # Ensure it's a Tag object
                    for row in tbody.find_all('tr'):
                        if isinstance(row, Tag):  # Ensure it's a Tag object
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                class_description.append(tds[1].get_text(strip=True))

            print(class_description)
            print(len(class_description))

        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

async def main():
    await scrape_detail_by_keyword("DID2022035944")

if __name__ == "__main__":
    asyncio.run(main())
