import requests
import json
import re
import os
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_car_details(title):
    pattern = r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s-]+)'
    match = re.match(pattern, title)
    if match:
        year = match.group(1)
        make = match.group(2)
        model = match.group(3).strip()
        return year, make, model
    return None, None, None

def get_cars_dot_com_listings(
    dataset_ids=None,
    token=None
):
    if dataset_ids is None:
        dataset_ids = [
            "etsbOifCMshuG5CfO"
        ]
    if token is None:
        token = os.getenv("APIFY_API_TOKEN")

    all_listings = []

    for dataset_id in dataset_ids:
        base_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        limit = 100
        offset = 0

        while True:
            url = f"{base_url}?format=json&clean=true&token={token}&limit={limit}&offset={offset}"
            response = requests.get(url, headers={"Accept": "application/json"})

            try:
                data = response.json()
            except json.JSONDecodeError:
                print(f"Failed to decode JSON at offset {offset}")
                break

            if not data:
                break

            for car in data:
                if isinstance(car, dict):
                    title = car.get("title", "")
                    year, make, model = extract_car_details(title)
                    # Fix for Rolls-Royce: extract make/model from title if missing
                    if (make is None or model is None) and "Rolls-Royce" in title:
                        parts = title.split()
                        if len(parts) >= 3:
                            make = parts[1] + "-" + parts[2].split("-")[0] if parts[2].startswith("Royce") else parts[1]
                            model = parts[3] if len(parts) > 3 else None
                    all_listings.append({
                        "title": title,
                        "vin": car.get("vin"),
                        "make": make,
                        "model": model,
                        "year": car.get("year", year),
                        "mileage": car.get("mileage"),
                        "price": car.get("price"),
                        "location": car.get("location"),
                        "contact_info": None,
                        "image_url": None,  # Will fill in next step
                        "listing_url": car.get("url")
                    })

            offset += limit

    return all_listings

def fetch_image_url_selenium(listing_url, wait_time=10):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Uncomment for headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    image_url = None
    try:
        driver.get(listing_url)
        driver.implicitly_wait(wait_time)
        img_tag = driver.find_element(By.CSS_SELECTOR, 'img.swipe-main-image.image-index-0')
        image_url = img_tag.get_attribute('src')
    except Exception as e:
        print(f"Error fetching image for {listing_url}: {e}")
    finally:
        driver.quit()
    return image_url

def fetch_image_for_car(car):
    url = car.get("listing_url")
    if url:
        car["image_url"] = fetch_image_url_selenium(url)
    return car

if __name__ == "__main__":
    listings = get_cars_dot_com_listings()
    print(f"\n✅ Scraped {len(listings)} listings from Apify. Now fetching images with Selenium (parallel)...")

    max_workers = 10  # Number of parallel browsers
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(fetch_image_for_car, car) for car in listings]
        for future in as_completed(futures):
            results.append(future.result())

    print(f"\n✅ Finished fetching images. Preview first 5 results:")
    for r in results[:5]:
        print(r)
