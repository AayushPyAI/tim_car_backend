from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

# Parse year, make, and model from title
def parse_title_fields(title: str):
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
                model_parts = []
                for j in range(i + 2, len(parts)):
                    if parts[j] == make:
                        break
                    model_parts.append(parts[j])
                model = " ".join(model_parts).strip()
                break
            except Exception:
                pass

    return year, make, model

# Step 1: Extract listing URLs and basic info
def get_listing_links(driver):
    driver.get("https://www.cars.com/shopping/results/?clean_title=true&dealer_id=&include_shippable=true")
    sleep(6)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.vehicle-card')

    for card in cards:
        try:
            title_elem = card.find_elements(By.CSS_SELECTOR, "h2.title")
            price_elem = card.find_elements(By.CSS_SELECTOR, "span.primary-price")
            link_elem = card.find_elements(By.CSS_SELECTOR, "a.vehicle-card-link")
            image_elem = card.find_elements(By.CSS_SELECTOR, "img.vehicle-image")
            location_elem = card.find_elements(By.CSS_SELECTOR, "div.miles-from")

            title = title_elem[0].text if title_elem else "N/A"
            price = price_elem[0].text.replace("$", "").replace(",", "") if price_elem else "0"
            url = link_elem[0].get_attribute("href") if link_elem else ""
            image_url = image_elem[0].get_attribute("src") if image_elem else ""
            location = location_elem[0].text if location_elem else "N/A"

            listings.append({
                "title": title,
                "price": float(price),
                "listing_url": url,
                "image_url": image_url,
                "location": location
            })
        except Exception as e:
            print("Error collecting basic info:", e)
    return listings

# Step 2: Visit each listing page and scrape detailed info
def get_detail_from_listing(driver, url):
    driver.get(url)
    sleep(3)

    details = {}
    try:
        dl = driver.find_element(By.CSS_SELECTOR, "dl.fancy-description-list")
        dt_tags = dl.find_elements(By.TAG_NAME, "dt")
        dd_tags = dl.find_elements(By.TAG_NAME, "dd")

        for dt, dd in zip(dt_tags, dd_tags):
            key = dt.text.strip().lower().replace(" ", "_")
            value = dd.text.strip()
            details[key] = value

        # Extract contact info (phone number)
        phone_elem = driver.find_elements(By.CSS_SELECTOR, "div.dealer-phone")
        details["contact_info"] = phone_elem[0].text if phone_elem else "N/A"

    except Exception as e:
        print(f"Error scraping detail page {url}:", e)
    return details

# Main scraper
def get_cars_dot_com_listings():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    listings_summary = get_listing_links(driver)

    detailed_listings = []
    for item in listings_summary[:3]:
        detail_data = get_detail_from_listing(driver, item["listing_url"])
        year, make, model = parse_title_fields(item["title"])

        listing = {
            "title": item["title"],
            "vin": detail_data.get("vin", "N/A"),
            "make": make or "Unknown",
            "model": model or "Unknown",
            "year": year or 0,
            "mileage": detail_data.get("mileage", "0").replace("mi.", "").replace(",", "").strip(),
            "price": item["price"],
            "location": item["location"],
            "contact_info": detail_data.get("contact_info", "N/A"),
            "image_url": item["image_url"],
            "listing_url": item["listing_url"],
        }

        detailed_listings.append(listing)

    driver.quit()
    return detailed_listings


if __name__ == "__main__":
    results = get_cars_dot_com_listings()
    print(f"\n✅ Scraped {len(results)} listings:")
    for r in results[:5]:  # Preview first 5
        print(r)
