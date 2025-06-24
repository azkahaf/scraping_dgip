import asyncio
from re import I
from bs4 import BeautifulSoup
from bs4.element import Tag
from playwright.async_api import async_playwright, expect
import csv

#Atribute
nomor_permohonan = []
tahun_permohonan = []
status = []
brand_tags = []
kode_kelas = []
class_description = []
mult_class_description = []
final_data = []

async def final_parsing():
        print("List lengths:")
        print("brand_tags:", len(brand_tags))
        print("nomor_permohonan:", len(nomor_permohonan))
        print("tahun_permohonan:", len(tahun_permohonan))
        print("status:", len(status))
        print("kode_kelas:", len(kode_kelas))
        print("class_description:", len(class_description))
    
        #====== MULTIPLE CLASS START HERE ======
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Step 1: Open search page
                await page.goto("https://pdki-indonesia.dgip.go.id/search", wait_until="networkidle")
                # print("Opened search page")

                # Step: Combine data into rows, repeating other fields based on number of kelas
                for idx in range(len(brand_tags)):
                    if idx >= len(kode_kelas):
                        row = {
                            "Brand": brand_tags[idx],
                            "Nomor Permohonan": nomor_permohonan[idx],
                            "Tahun Permohonan": tahun_permohonan[idx],
                            "Status": status[idx],
                            "Kode Kelas": "",
                            "Deskripsi Kelas": ""
                        }
                        # Append to final structured list
                        final_data.append(row)
                    else:
                        # Get list of class codes for this brand
                        current_classes = kode_kelas[idx] if isinstance(kode_kelas[idx], list) else [kode_kelas[idx]]

                        if len(current_classes) == 1:
                            row = {
                                "Brand": brand_tags[idx],
                                "Nomor Permohonan": nomor_permohonan[idx],
                                "Tahun Permohonan": tahun_permohonan[idx],
                                "Status": status[idx],
                                "Kode Kelas": kode_kelas[idx],
                                "Deskripsi Kelas": class_description[idx]
                            }
                            # Append to final structured list
                            final_data.append(row)
                        else:
                            mult_class_description = []
                            # Step 2: Enter keyword and search
                            await page.fill("input >> nth=0", nomor_permohonan[idx])
                            await asyncio.sleep(1)
                            await page.keyboard.press("Enter")
                            # print(f"Searching for: {nomor_permohonan[idx]}")

                            # Step 3: Click the first result
                            await page.wait_for_selector('a[href^="/link/"]', timeout=20000)
                            await asyncio.sleep(1)
                            await page.click('a[href^="/link/"]')
                            # print("Clicked the first search result")

                            # Step 4: Wait for detail page to load
                            await page.wait_for_selector('text=Nomor Registrasi', timeout=20000)
                            # print("Detail page loaded")

                            # Step 5: Scrape HTML content
                            content = await page.content()
                            soup = BeautifulSoup(content, 'html.parser')

                            #Parse deskripsi kelas
                            # Always iterate over results of find_all
                            for tbody in soup.find_all('tbody'):
                                if isinstance(tbody, Tag):  # Ensure it's a Tag object
                                    for row in tbody.find_all('tr'):
                                        if isinstance(row, Tag):  # Ensure it's a Tag object
                                            tds = row.find_all('td')
                                            if len(tds) >= 2:
                                                mult_class_description.append(tds[1].get_text(strip=True))

                            for i in range(len(mult_class_description)):
                                row = {
                                "Brand": brand_tags[idx],
                                "Nomor Permohonan": nomor_permohonan[idx],
                                "Tahun Permohonan": tahun_permohonan[idx],
                                "Status": status[idx],
                                "Kode Kelas": current_classes[i],
                                "Deskripsi Kelas": mult_class_description[i]
                                }
                                # Append to final structured list
                                final_data.append(row)
                        
            #====== MULTIPLE CLASS END HERE ======

            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                await browser.close()
            
        with open('output_final.csv', 'w', newline='', encoding='utf-8') as csvfile:
            if final_data:
                fieldnames = ['No'] + list(final_data[0].keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for idx, row in enumerate(final_data, start=1):
                    row_with_index = {'No': idx, **row}
                    writer.writerow(row_with_index)

async def scrape_and_navigate_pagination(url, target_page_number):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle') 
            # print("Page loaded successfully.")

            # --- START OF FILTERING LOGIC ---
            # print("Applying the 'Didaftar' filter with a more precise method...")
            didaftar_checkbox = page.locator("label:has-text('Didaftar')").locator("..").locator("button[role='checkbox']")
            # print("Found checkbox. Attempting to check it...")
            await didaftar_checkbox.check()
            await expect(didaftar_checkbox).to_be_checked(timeout=5000)
            # print("Verification successful: Checkbox is now checked.")

            # print("Waiting for results to update after filtering...")
            await page.wait_for_load_state('networkidle', timeout=30000)
            # print("Filter applied and results are loaded.")
            
            await page.screenshot(path='verified_filter_applied.png')
            # print("Saved screenshot 'verified_filter_applied.png'. Please check it.")
            # --- END OF FILTERING LOGIC ---

            # --- Wait for the pagination controls to be visible on the filtered page ---
            await page.get_by_text("1", exact=True).wait_for(state='visible', timeout=15000)
            # print("Pagination controls found on filtered page.")

            

            # Now, loop through the remaining pages
            for i in range(1, target_page_number + 1):
                # print("-" * 20)
                page_button_selector = page.get_by_role("button", name=str(i), exact=True)
                
                # print(f"Attempting to click page '{i}' button...")
                await page_button_selector.click()
                # print(f"Clicked page '{i}' button.")

                # print("Waiting for new page content to load...")
                await page.wait_for_load_state('networkidle', timeout=30000)
                await asyncio.sleep(2)

                # print(f"Page {i} loaded. Extracting HTML...")
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # ======= START OF PARSING =======

                #Parse kode kelas
                kode_kelas_raw = soup.find_all('p', class_="text-sm")
                for each in kode_kelas_raw:
                    temp_kode_kelas = each.get_text(strip=True)
                    if "Kode kelas: " in temp_kode_kelas:
                        temp_fix_class = temp_kode_kelas.replace("Kode kelas: ", "").split(",")
                        kode_kelas.append(temp_fix_class[0])
                # print(kode_kelas)

                #Parse nomor permohonan
                nomor_permohonan_raw = soup.find_all('p', class_='text-gray-400 font-medium text-sm')
                for each in nomor_permohonan_raw:
                    temp_nomor_permohonan = each.get_text(strip=True)
                    nomor_permohonan.append(temp_nomor_permohonan)
                    tahun_permohonan.append(temp_nomor_permohonan[3:7])
                # print(nomor_permohonan)
                # print(tahun_permohonan)

                #Parse Nama Merek
                brand_tags_raw = soup.find_all('h1', class_='text-md md:text-lg cursor-pointer')
                for each in brand_tags_raw:
                    brand_name = each.get_text(strip=True)
                    brand_tags.append(brand_name)
                # print(brand_tags)

                #Parse status
                for each in brand_tags_raw:
                    status.append("Didaftar")
                # print(status)

                #Parse deskripsi kelas
                class_description_raw = soup.find_all('p', class_="text-gray-400 font-medium text-sm line-clamp-1 text-ellipsis w-full")
                for each in class_description_raw:
                    temp_class_description = each.get_text(strip=True)
                    class_description.append(temp_class_description)
                # print(class_description)

                # ======= END OF PARSING =======

                # output_filename = f'scraped_page_{i}.txt'
                # with open(output_filename, 'w', encoding='utf-8') as f:
                #     f.write(str(soup.prettify()))
                # # print(f"Data parsed")

                screenshot_filename = f'scraped_page_{i}.png'
                await page.screenshot(path=screenshot_filename, full_page=True)
                print(f"Screenshot saved to {screenshot_filename}")

        except Exception as e:
            # print(f"An error occurred: {e}")
            await page.screenshot(path='error_screenshot.png')
            # print("Saved 'error_screenshot.png' for debugging.")
        finally:
            await browser.close()
            # print("Browser closed.")

async def main_playwright():
    url_to_scrape = "https://pdki-indonesia.dgip.go.id/search"
    await scrape_and_navigate_pagination(url_to_scrape, 100) 
    await final_parsing()

if __name__ == '__main__':
    asyncio.run(main_playwright())