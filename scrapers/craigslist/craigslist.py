from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

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
        if part.isdigit() and len(part) == 4 and 1980 <= int(part) <= 2026:
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

def enrich_listing_details(driver, listing):
    try:
        driver.get(listing['listing_url'])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "postingbody"))
        )
        body = driver.find_element(By.ID, "postingbody").text

        for line in body.splitlines():
            line = line.strip()
            if line.lower().startswith("year:"):
                listing["year"] = int(line.split(":", 1)[1].strip())
            elif line.lower().startswith("make:"):
                listing["make"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("model:"):
                listing["model"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("vin:"):
                listing["vin"] = line.split(":", 1)[1].strip()
            elif line.lower().startswith("mileage:"):
                try:
                    raw = line.split(":", 1)[1].strip().lower().replace("mi", "").replace(",", "")
                    listing["mileage"] = float(raw)
                except:
                    pass

        # Fallback: parse title if any field is still missing
        if listing["year"] == 2020 or listing["make"] == "Unknown" or listing["model"] == "Unknown":
            parsed_year, parsed_make, parsed_model = parse_title_fields(listing["title"])
            if listing["year"] == 2020 and parsed_year:
                listing["year"] = parsed_year
            if listing["make"] == "Unknown" and parsed_make:
                listing["make"] = parsed_make
            if listing["model"] == "Unknown" and parsed_model:
                listing["model"] = parsed_model

    except Exception as e:
        print(f"Error enriching listing {listing['listing_url']}: {e}")

def get_craigslist_listings():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = "https://dallas.craigslist.org/search/cta?isTrusted=true&max_auto_miles=50000&min_auto_year=2016&min_price=20000&purveyor=owner#search=2~gallery~0"
    driver.get(url)
    sleep(5)  # Let JS load

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.gallery-card')

    for card in cards[:3]:
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, 'a.posting-title span.label')
            price_elem = card.find_element(By.CSS_SELECTOR, 'span.priceinfo')
            link_elem = card.find_element(By.CSS_SELECTOR, 'a.posting-title')
            meta_elem = card.find_element(By.CSS_SELECTOR, 'div.meta-line div.meta')

            title = title_elem.text.strip()
            price = price_elem.text.strip().replace("$", "").replace(",", "")
            link = link_elem.get_attribute("href")
            meta_text = meta_elem.text.strip()

            meta_parts = [part.strip() for part in meta_text.splitlines()]
            location = meta_parts[-1] if meta_parts else "Unknown"
            mileage = 0.0

            image_url = ""
            try:
                img_tag = card.find_element(By.CSS_SELECTOR, "div.swipe img")
                image_url = img_tag.get_attribute("src")
            except:
                pass

            for part in meta_parts:
                if "mi" in part.lower():
                    try:
                        mileage = float(part.lower().replace("mi", "").replace("k", "000").replace(",", "").strip())
                    except ValueError:
                        pass
                elif "tx" in part.lower():
                    location = part

            listing = {
                "title": title,
                "vin": "N/A",
                "make": "Unknown",
                "model": "Unknown",
                "year": 2020,
                "mileage": mileage,
                "price": float(price),
                "location": location,
                "contact_info": "Craigslist Contact",
                "image_url": image_url,
                "listing_url": link
            }

            listings.append(listing)

        except Exception as e:
            print("Error parsing listing:", e)

    print(f"Front listings scraped: {len(listings)}. Now enriching from detail pages...\n")

    for listing in listings:
        enrich_listing_details(driver, listing)

    driver.quit()
    return listings

# if __name__ == "__main__":
#     results = get_craigslist_listings()
#     print(f"Final enriched listings: {len(results)}\n")
#     for item in results[:10]:
#         print(item)
