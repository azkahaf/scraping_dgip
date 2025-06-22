import asyncio
from re import I
from playwright.async_api import async_playwright

async def scrape_and_navigate_pagination(url, target_page_number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) #Keep headless=False for debugging
        page = await browser.new_page()
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle') 
            print("Page loaded. Waiting for initial content...")

            # --- Wait for the pagination controls to be visible ---
            # It's good practice to wait for some element on the page, like the current page number
            await page.get_by_text(str(1), exact=True).wait_for(state='visible', timeout=15000)
            print("Pagination controls found.")

            for i in range(1, target_page_number):
                #Attempting Step 1: Click the target page number button
                print(f"Attempting to click page '{i}' button...")

                # This is the most direct way to click a button by its exact text content.
                # The `exact=True` ensures it only matches "2", not "20" or "123".
                page_button_selector = page.get_by_role("button", name=str(i), exact=True)

                #Click the page button
                await page_button_selector.click()
                print(f"Clicked page '{i}' button.")

                #Wait for the new page content to load
                print("Waiting for new page content to load...")
                await page.wait_for_load_state('networkidle', timeout=30000) # Increased timeout
                await asyncio.sleep(3) # A small, optional delay if content loads very slowly

                print(f"Page {i} loaded. Extracting HTML...")
                content = await page.content()

                # Save the HTML to a file
                output_filename = f'flash_page_{i}.txt'
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Data saved to {output_filename}")

                # Take a screenshot of the new page
                screenshot_filename = f'scraped_page_{i}.png'
                await page.screenshot(path=screenshot_filename, full_page=True)
                print(f"Screenshot saved to {screenshot_filename}")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()
            print("Browser closed.")

async def main_playwright():
    url_to_scrape = "https://pdki-indonesia.dgip.go.id/search"
    await scrape_and_navigate_pagination(url_to_scrape, 10) 

if __name__ == '__main__':
    asyncio.run(main_playwright())