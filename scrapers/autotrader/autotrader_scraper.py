import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep


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
    # chrome_options.add_argument("--headless")  # Enable this when running headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.autotrader.com/cars-for-sale/by-owner/plano-tx?searchRadius=0&zip=75023")
    sleep(6)  # Let JS content load

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
            sleep(5)

            # Extract VIN
            vin_elem = driver.find_elements(By.CSS_SELECTOR, 'div[data-cmp="section"] .text-gray-dark')
            vin_text = vin_elem[0].text if vin_elem else ""
            vin_match = re.search(r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})', vin_text)
            listing["vin"] = vin_match.group(1) if vin_match else None

            # Extract Location
            location_container = driver.find_elements(By.CSS_SELECTOR, 'div.display-flex.align-items-center.flex-wrap.gap-2')
            if location_container:
                span_elems = location_container[0].find_elements(By.TAG_NAME, "span")
                listing["location"] = span_elems[0].text.strip() if span_elems else None

        except Exception as e:
            print(f"Error scraping details from {listing.get('listing_url')}: {e}")

    driver.quit()
    return listings


if __name__ == "__main__":
    results = get_autotrader_listings()
    print(f"Found {len(results)} listings:\n")
    for item in results[:60]:
        print(item)
