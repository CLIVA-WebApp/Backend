import asyncio
import json
import os
from datetime import datetime
from playwright.async_api import async_playwright

# Logging setup
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
os.makedirs("logs", exist_ok=True)
log_file_path = f"logs/{timestamp}.log"

# Create download folder
os.makedirs("regency_csv", exist_ok=True)

def log(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{now}  [INFO]  {message}"
    print(line)
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

async def scrape():
    # Load regency list
    with open("regency_list.json", "r", encoding="utf-8") as f:
        regencies = json.load(f)

    async with async_playwright() as p:
        # Set up browser with download handling
        browser = await p.chromium.launch(headless=False)  # Set headless=True if you want no GUI
        context = await browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Set up download path
        download_path = os.path.abspath("regency_csv")
        await context.set_extra_http_headers({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        })

        for regency in regencies:
            regency_name = regency["name"].lower().replace(" ", "")
            province_id = regency["province_id"]

            log(f"Processing regency: {regency['name']} (Province ID: {province_id})")

            found_valid = False

            for suffix in ["kab", "kota"]:
                subdomain = f"{regency_name}{suffix}"
                subject_url = f"https://{subdomain}.bps.go.id/id/statistics-table?subject=519"

                try:
                    log(f"Trying URL: {subject_url}")
                    await page.goto(subject_url, timeout=15000)

                    # Handle popup if it exists
                    try:
                        # Look for the "Tutup" button to close popup
                        tutup_button = page.locator("button:has-text('Tutup')")
                        if await tutup_button.is_visible():
                            log("Found popup, clicking 'Tutup' button to close it")
                            await tutup_button.click()
                            await page.wait_for_load_state("networkidle")
                    except Exception as e:
                        log(f"No popup found or failed to close: {e}")

                    # Look for table rows with multiple keyword options
                    rows = await page.locator("table tr").all()
                    
                    # Keywords to search for (case-insensitive)
                    keywords = ["per kecamatan", "menurut kecamatan", "rasio"]
                    
                    target_row = None
                    for row in rows:
                        text = await row.inner_text()
                        text_lower = text.lower()
                        
                        # Check if any keyword is found in this row
                        if any(keyword in text_lower for keyword in keywords):
                            target_row = row
                            log(f"Found matching row with keywords: {text.strip()}")
                            break

                    if not target_row:
                        log(f"No matching row found with keywords {keywords} in {subdomain}")
                        continue

                    log(f"Clicking matching row on {subdomain}")
                    await target_row.click()
                    await page.wait_for_load_state("networkidle")
                    
                    # Wait for navigation to complete
                    await page.wait_for_timeout(3000)  # Wait for page to fully load
                    current_url = page.url
                    log(f"Navigated to data page: {current_url}")

                    # Handle year selection through dropdown or button
                    try:
                        # First try to find the year dropdown container
                        year_container = page.locator("div.css-b62m3t-container")
                        if await year_container.is_visible():
                            log("Found year dropdown, clicking to open it")
                            await year_container.click()
                            await page.wait_for_timeout(1000)  # Wait for dropdown to appear
                            
                            # Look for the 2023 option in the dropdown menu
                            year_2023_option = page.locator("div.css-8aqfg3-menu div:has-text('2023')")
                            if await year_2023_option.is_visible():
                                log("Found 2023 option in dropdown, clicking it")
                                await year_2023_option.click()
                                await page.wait_for_load_state("networkidle")
                                await page.wait_for_timeout(2000)  # Wait for data to load
                                log("Year changed to 2023 via dropdown")
                            else:
                                log("2023 option not found in dropdown")
                        else:
                            # If no dropdown, try to find the 2023 button
                            year_2023_button = page.locator("button:has-text('2023')")
                            if await year_2023_button.is_visible():
                                log("Found 2023 button, clicking it")
                                await year_2023_button.click()
                                await page.wait_for_load_state("networkidle")
                                await page.wait_for_timeout(2000)  # Wait for data to load
                                log("Year changed to 2023 via button")
                            else:
                                log("Neither dropdown nor 2023 button found")
                    except Exception as e:
                        log(f"Failed to change year to 2023: {e}")

                    # Check for React error
                    content = await page.content()
                    if "Minified React error #185" in content:
                        log(f"❌ Data for year 2023 not available (React 185 error) — skipping")
                        continue

                    # Try clicking the "Unduh" button and download CSV
                    try:
                        # Look for the Unduh button with the specific class and structure
                        unduh_button = page.locator("button:has-text('Unduh')")
                        if await unduh_button.is_visible():
                            log("Found Unduh button, clicking it")
                            
                            await unduh_button.click()
                            await page.wait_for_timeout(2000)  # Wait for dropdown to appear
                            
                            # Look for the CSV button with the specific class
                            csv_button = page.locator("button.download-product:has-text('CSV')")
                            if await csv_button.is_visible():
                                log("Found CSV button, clicking it")
                                await csv_button.click()
                                
                                # Wait for download to complete
                                await page.wait_for_timeout(5000)  # Wait 5 seconds for download
                                log(f"✅ CSV download triggered for {regency['name']} - check browser downloads")
                                found_valid = True
                                break  # No need to try other suffix
                            else:
                                log("CSV button not found in dropdown")
                        else:
                            log("Unduh button not found")
                            
                    except Exception as e:
                        log(f"⚠️ Failed to trigger CSV download: {e}")
                    finally:
                        await asyncio.sleep(10)

                except Exception as e:
                    log(f"⚠️ Failed to access {subject_url}: {e}")
                finally:
                    await asyncio.sleep(10)

            if not found_valid:
                log(f"🔍 No valid data found for {regency['name']}, skipping...\n")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape())
