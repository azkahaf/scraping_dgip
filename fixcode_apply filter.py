import asyncio
from re import I
from playwright.async_api import async_playwright, expect

async def scrape_and_navigate_pagination(url, target_page_number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle') 
            print("Page loaded successfully.")

            # --- REVISED FILTERING LOGIC ---
            print("Applying the 'Didaftar' filter with a more precise method...")

            # 1. Locate the button right next to the label 'Didaftar'
            # This is a very robust selector: it finds the button based on the visible text nearby.
            # The '..' selector goes to the parent element of the label, then we find the button inside it.
            didaftar_checkbox = page.locator("label:has-text('Didaftar')").locator("..").locator("button[role='checkbox']")
            
            # 2. Use the .check() action, which is designed for checkboxes.
            # It's more reliable than .click() for this purpose.
            print("Found checkbox. Attempting to check it...")
            await didaftar_checkbox.check()

            # 3. VERIFY the action. This is a best practice.
            # We expect the checkbox to be in a 'checked' state. Playwright will wait a bit for this to happen.
            # If this line fails, we know the check action was unsuccessful.
            await expect(didaftar_checkbox).to_be_checked(timeout=5000)
            print("Verification successful: Checkbox is now checked.")

            # 4. Wait for the page to update after the successful and verified action.
            print("Waiting for results to update after filtering...")
            await page.wait_for_load_state('networkidle', timeout=30000)
            print("Filter applied and results are loaded.")
            
            await page.screenshot(path='verified_filter_applied.png')
            print("Saved screenshot 'verified_filter_applied.png'. Please check it.")
            # --- END OF REVISED LOGIC ---

            # --- Wait for the pagination controls to be visible on the filtered page ---
            await page.get_by_text("1", exact=True).wait_for(state='visible', timeout=15000)
            print("Pagination controls found on filtered page.")

            # First, save the data for the already loaded page 1
            print("Page 1 is loaded. Extracting HTML...")
            content_page_1 = await page.content()
            with open('flash_page_1.txt', 'w', encoding='utf-8') as f:
                f.write(content_page_1)
            print("Data saved to flash_page_1.txt")
            await page.screenshot(path='scraped_page_1.png', full_page=True)
            print("Screenshot saved to scraped_page_1.png")


            # Now, loop through the remaining pages
            for i in range(2, target_page_number + 1):
                print("-" * 20)
                page_button_selector = page.get_by_role("button", name=str(i), exact=True)
                
                print(f"Attempting to click page '{i}' button...")
                await page_button_selector.click()
                print(f"Clicked page '{i}' button.")

                print("Waiting for new page content to load...")
                await page.wait_for_load_state('networkidle', timeout=30000)
                await asyncio.sleep(2)

                print(f"Page {i} loaded. Extracting HTML...")
                content = await page.content()

                output_filename = f'flash_page_{i}.txt'
                with open(output_filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Data saved to {output_filename}")

                screenshot_filename = f'scraped_page_{i}.png'
                await page.screenshot(path=screenshot_filename, full_page=True)
                print(f"Screenshot saved to {screenshot_filename}")

        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path='error_screenshot.png')
            print("Saved 'error_screenshot.png' for debugging.")
        finally:
            await browser.close()
            print("Browser closed.")

async def main_playwright():
    url_to_scrape = "https://pdki-indonesia.dgip.go.id/search"
    await scrape_and_navigate_pagination(url_to_scrape, 10) 

if __name__ == '__main__':
    asyncio.run(main_playwright())