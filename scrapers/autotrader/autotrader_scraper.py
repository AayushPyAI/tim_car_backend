import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from bs4 import BeautifulSoup
import time


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


def get_listing_summaries_from_url(url, seen_ids):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print(f"[LOG] Fetching page: {url}")
    listings = []
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-cmp=\"itemCard\"]'))
        )
    except Exception as e:
        driver.quit()
        return listings

    # Wait for all cards to load (stabilize)
    last_count = 0
    stable_count = 0
    for _ in range(20):  # up to 20 seconds
        cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-cmp="itemCard"]')
        if len(cards) == last_count:
            stable_count += 1
        else:
            stable_count = 0
        if stable_count >= 3:  # stable for 3 seconds
            break
        last_count = len(cards)
        time.sleep(1)

    cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-cmp="itemCard"]')
    print(f"[LOG] Found {len(cards)} cards on this page")
    for card in cards:
        try:
            # Try to get the id from the card itself
            listing_id = card.get_attribute("id")
            # If not present, try the parent inventorySpotlightListing
            if not listing_id:
                try:
                    parent = card.find_element(By.XPATH, './ancestor::div[@data-cmp="inventorySpotlightListing"]')
                    listing_id = parent.get_attribute("id")
                except Exception:
                    listing_id = None
            # As a last resort, use the href of the detail link
            if not listing_id:
                try:
                    link_elem = card.find_element(By.CSS_SELECTOR, 'a[data-cmp="link"]')
                    raw_href = link_elem.get_attribute("href")
                    if raw_href:
                        listing_id = raw_href.split('/')[-1].split('?')[0]
                except Exception:
                    listing_id = None
            if not listing_id or listing_id in seen_ids:
                continue
            seen_ids.add(listing_id)
            title_elem = card.find_elements(By.CSS_SELECTOR, 'h2[data-cmp="subheading"]')
            title = title_elem[0].text.strip() if title_elem else None
            print(f"[LOG] Card title: {title}")
            year, make, model = parse_title_fields(title)
            price_elem = card.find_elements(By.CSS_SELECTOR, 'div[data-cmp="firstPrice"]')
            price_text = price_elem[0].text if price_elem else None
            price = float(price_text.replace(",", "").replace("$", "")) if price_text else None
            image_elem = card.find_elements(By.CSS_SELECTOR, 'img[data-cmp="inventoryImage"]')
            image_url = image_elem[0].get_attribute("src") if image_elem else None
            mileage_elem = card.find_elements(By.CSS_SELECTOR, 'div[data-cmp="mileageSpecification"]')
            mileage_text = mileage_elem[0].text if mileage_elem else None
            mileage = float(mileage_text.replace(",", "").replace("miles", "").strip()) if mileage_text else None
            # Build detail URL
            detail_url = f"https://www.autotrader.com/cars-for-sale/vehicle/{listing_id}?city=Plano&listingType=USED&makeCode=BENTL&makeCode=FER&makeCode=LAM&makeCode=MCLAREN&makeCode=POR&searchRadius=0&sellerType=p&state=TX&zip=75023&clickType=listing"
            listing = {
                "id": listing_id,
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
                "listing_url": detail_url
            }
            # Only add if we have a valid id and title
            if listing_id and title:
                listings.append(listing)
        except Exception:
            continue
    driver.quit()
    return listings


def get_autotrader_listings():
    all_listings = []
    seen_ids = set()
    page_size = 25  # Adjust if needed
    # Only go up to firstRecord=50 (i.e., 0, 25, 50)
    for first_record in range(0, 100, page_size):
        url = f"https://www.autotrader.com/cars-for-sale/by-owner/plano-tx?firstRecord={first_record}&makeCode=BENTL&makeCode=FER&makeCode=LAM&makeCode=MCLAREN&makeCode=POR&searchRadius=0&zip=75023"
        listings = get_listing_summaries_from_url(url, seen_ids)
        if not listings:
            print(f"[LOG] No more listings found at firstRecord={first_record}, stopping.")
            break
        all_listings.extend(listings)
        print(f"[LOG] Total listings collected so far: {len(all_listings)}")
    return all_listings


def fetch_detail_info(listing):
    url = listing["listing_url"]
    print(f"[DETAIL] Fetching (selenium): {url}")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    prefs = {
        "profile.managed_default_content_settings.images": 2,
        "profile.managed_default_content_settings.stylesheets": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    try:
        driver.get(url)
        # Wait for the sellerComments section or body to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sellerComments"))
            )
            print("[DEBUG] sellerComments section loaded.")
        except Exception:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            print("[DEBUG] Body loaded as fallback.")
        # For debugging: keep the browser open for 3 seconds
        time.sleep(3)
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
        if listing["vin"]:
            print(f"[DETAIL] VIN found for {url}: {listing['vin']}")
        else:
            print(f"[DETAIL] VIN NOT found for {url}")
        # Location extraction (unchanged)
        location = None
        try:
            loc_elem = driver.find_element(By.CSS_SELECTOR, 'div[data-cmp="psxOwnerDetailsSnapshot"] span')
            if loc_elem and "," in loc_elem.text:
                location = loc_elem.text.strip()
        except Exception:
            pass
        if not location:
            try:
                loc_elem2 = driver.find_element(By.CSS_SELECTOR, 'div[data-cmp="ownerLocation"] span')
                if loc_elem2 and "," in loc_elem2.text:
                    location = loc_elem2.text.strip()
            except Exception:
                pass
        listing["location"] = location
        if location:
            print(f"[DETAIL] Location found for {url}: {location}")
        else:
            print(f"[DETAIL] Location NOT found for {url}")
    except Exception as e:
        print(f"[DETAIL] Exception for {url}: {e}")
    finally:
        driver.quit()
    return listing


# if __name__ == "__main__":
#     summaries = get_autotrader_listings()
#     print(f"Found {len(summaries)} listings:")
#     from concurrent.futures import ThreadPoolExecutor, as_completed
#     results = []
#     def safe_fetch_detail(listing):
#         print(f"[DEBUG] Starting detail scrape for: {listing['listing_url']}")
#         try:
#             return fetch_detail_info(listing)
#         except Exception as e:
#             print(f"[ERROR] Exception in detail scraping for {listing['listing_url']}: {e}")
#             return listing
#     with ThreadPoolExecutor(max_workers=2) as executor:  # You can increase max_workers for more parallelism
#         future_to_listing = {executor.submit(safe_fetch_detail, l): l for l in summaries}
#         for future in as_completed(future_to_listing):
#             result = future.result()
#             results.append(result)
#     for item in results:
#         print(item)
