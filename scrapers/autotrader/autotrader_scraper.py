import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def parse_title_fields(title: str):
    """
    Extract year, make, and model from title like 'Used 2017 Porsche Macan GTS'
    """
    if not title:
        return None, None, None

    parts = title.split()
    if len(parts) < 3:
        return None, None, None

    year = None
    make = None
    model = None

    for i, part in enumerate(parts):
        if part.isdigit() and len(part) == 4:
            try:
                year = int(part)
                make = parts[i + 1] if i + 1 < len(parts) else None
                model = ' '.join(parts[i + 2:]) if i + 2 < len(parts) else None
                break
            except (IndexError, ValueError):
                return None, None, None

    return year, make, model


def get_autotrader_listings():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Enable this when running headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Add arguments to make scraper appear more human
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Disable images and CSS for faster loading
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    driver.get("https://www.autotrader.com/cars-for-sale/by-owner/plano-tx?marketExtension=off&searchRadius=0&zip=75023...it")
    # Wait for cards to load instead of fixed sleep
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cmp="itemCard"]'))
        )
    except Exception as e:
        print("Timeout waiting for main page to load:", e)
        driver.quit()
        return []

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-cmp="itemCard"]')

    for card in cards:
        try:
            title_elem = card.find_elements(By.CSS_SELECTOR, 'h2[data-cmp="subheading"]')
            title = title_elem[0].text.strip() if title_elem else None

            year, make, model = parse_title_fields(title)

            price_elem = card.find_elements(By.CSS_SELECTOR, 'div[data-cmp="firstPrice"]')
            price_text = price_elem[0].text if price_elem else None
            price = float(price_text.replace(",", "").replace("$", "")) if price_text else None

            link_elem = card.find_elements(By.CSS_SELECTOR, 'a[data-cmp="link"]')
            raw_href = link_elem[0].get_attribute("href") if link_elem else None
            url = raw_href if raw_href and raw_href.startswith("http") else (
                "https://www.autotrader.com" + raw_href if raw_href else None
            )

            image_elem = card.find_elements(By.CSS_SELECTOR, 'img[data-cmp="inventoryImage"]')
            image_url = image_elem[0].get_attribute("src") if image_elem else None

            mileage_elem = card.find_elements(By.CSS_SELECTOR, 'div[data-cmp="mileageSpecification"]')
            mileage_text = mileage_elem[0].text if mileage_elem else None
            mileage = float(mileage_text.replace(",", "").replace("miles", "").strip()) if mileage_text else None

            listing = {
                "title": title,
                "vin": None,
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": price,
                "location": None,  # Will extract from detail page
                "contact_info": "Autotrader internal chat",
                "image_url": image_url,
                "listing_url": url
            }
            listings.append(listing)

        except Exception as e:
            print("Error parsing card:", e)

    # Visit each listing page to extract VIN and Location
    for listing in listings:
        try:
            listing_url = listing["listing_url"]
            if not listing_url:
                continue

            driver.get(listing_url)
            # Wait for VIN to be present on the page
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'VIN')]"))
                )
            except Exception as e:
                print(f"Timeout waiting for VIN on detail page {listing_url}:", e)
                continue

            # Initialize VIN and Location to ensure they are reset for each listing
            listing["vin"] = None
            listing["location"] = None

            # --- VIN Scraping: Try all known methods ---

            # Method 1: Check in the 'sellerComments' section
            try:
                vin_element = driver.find_element(By.XPATH, "//div[@id='sellerComments']//span[contains(., 'VIN:')]")
                vin_text = vin_element.text
                vin_match = re.search(r'([A-HJ-NPR-Z0-9]{17})', vin_text)
                if vin_match:
                    listing["vin"] = vin_match.group(1)
            except Exception:
                pass  # VIN not found with this method, continue

            # Method 2: Fallback to a page-wide regex search if still not found
            if not listing["vin"]:
                try:
                    vin_match = re.search(r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})', driver.page_source)
                    if vin_match:
                        listing["vin"] = vin_match.group(1)
                except Exception:
                    pass # VIN not found here either

            # --- Location Scraping: Try all known methods ---

            # Method 1: Check in the 'psxOwnerDetailsSnapshot' section
            try:
                location_element = driver.find_element(By.XPATH, "//div[@data-cmp='psxOwnerDetailsSnapshot']//span[contains(., ',')]")
                listing["location"] = location_element.text.strip()
            except Exception:
                pass  # Location not found with this method, continue

            # Method 2: Check for the older 'ownerLocation' format if still not found
            if not listing["location"]:
                try:
                    location_elem = driver.find_element(By.CSS_SELECTOR, "div[data-cmp='ownerLocation'] span")
                    listing["location"] = location_elem.text.strip()
                except Exception:
                    pass  # Location not found, will remain None

        except Exception as e:
            print(f"Error scraping details from {listing.get('listing_url')}: {e}")

    driver.quit()
    return listings


if __name__ == "__main__":
    results = get_autotrader_listings()
    print(f"Found {len(results)} listings:\n")
    for item in results:
        print(item)
