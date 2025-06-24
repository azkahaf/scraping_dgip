import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

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

            # ======= START OF PARSING =======

            #Parse nomor permohonan
            nomor_permohonan_raw = soup.find_all('p', class_='text-gray-400 font-medium text-sm')
            nomor_permohonan = []
            tahun_permohonan = []
            for each in nomor_permohonan_raw:
                temp_nomor_permohonan = each.get_text(strip=True)
                nomor_permohonan.append(temp_nomor_permohonan)
                tahun_permohonan.append(temp_nomor_permohonan[3:7])
            print(nomor_permohonan)
            print(tahun_permohonan)

            #Parse Nama Merek
            brand_tags_raw = soup.find_all('h1', class_='text-md md:text-lg cursor-pointer')
            brand_tags = []
            for each in brand_tags_raw:
                brand_name = each.get_text(strip=True)
                brand_tags.append(brand_name)
            print(brand_tags)

            #Parse kode kelas
            kode_kelas_raw = soup.find_all('p', class_="text-sm")
            kode_kelas = []
            for each in kode_kelas_raw:
                temp_kode_kelas = each.get_text(strip=True)
                if "Kode kelas: " in temp_kode_kelas:
                    kode_kelas.append(temp_kode_kelas.replace("Kode kelas: ", ""))
            print(kode_kelas)

            #Parse status
            status_raw = soup.find_all('div', class_="inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-yellow-200 text-yellow-700 hover:bg-yellow-200")
            status = []
            for each in status_raw:
                temp_status = each.get_text(strip=True)
                status.append(temp_status.replace("(TM) ", ""))
            print(status)

            #Parse deskripsi kelas
            class_description_raw = soup.find_all('p', class_="text-gray-400 font-medium text-sm line-clamp-1 text-ellipsis w-full")
            class_description = []
            for each in class_description_raw:
                temp_class_description = each.get_text(strip=True)
                class_description.append(temp_class_description)
            print(class_description)
            print(len(class_description))

            # ======= END OF PARSING =======
            
            # # Save to txt file
            # with open('scraped_page.txt', 'w', encoding='utf-8') as f:
            #     f.write(str(soup.prettify()))
            # print("Data saved")

            # # Take a screenshot to track progress
            # await page.screenshot(path='scraped_page.png', full_page=True)
            # print("Screenshoted")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

async def main_playwright():
    url = "https://pdki-indonesia.dgip.go.id/search"
    await scrape_with_playwright(url)

if __name__ == '__main__':
    asyncio.run(main_playwright())