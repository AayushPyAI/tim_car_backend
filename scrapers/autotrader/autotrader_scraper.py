import requests
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

def extract_car_details(title):
    pattern = r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s-]+)'
    match = re.match(pattern, title)
    if match:
        year = match.group(1)
        make = match.group(2)
        model = match.group(3).strip()
        return year, make, model
    return None, None, None

def extract_mileage(description):
    pattern = r'(\d{1,3}(?:,\d{3})*)\s*mi'
    match = re.search(pattern, description)
    if match:
        return match.group(1).replace(',', '')
    return None

def extract_location(url):
    pattern = r'zip=(\d{5})'
    match = re.search(pattern, url)
    if match:
        return f"Zip: {match.group(1)}"
    return None

def get_autotrader_listings(dataset_ids=None, token=None):
    if dataset_ids is None:
        dataset_ids = [
            "yzQNOu3JsLDz25kCk",  # Autotrader dataset ID
            "KrzhrZLEg4gBX8cmA",  # Additional Autotrader dataset ID
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
            except json.JSONDecodeError as e:
                break

            if not data:
                break

            for car in data:
                if isinstance(car, dict):
                    # Convert mileage to float if possible, else None
                    mileage = car.get("mileage")
                    if mileage:
                        try:
                            mileage = float(mileage.replace(",", ""))
                        except Exception:
                            mileage = None
                    images = car.get("images", [])
                    image_url = images[0] if images else None
                    all_listings.append({
                        "title": car.get("title"),
                        "vin": car.get("vin"),
                        "make": car.get("brand"),
                        "model": car.get("model"),
                        "year": car.get("year"),
                        "mileage": mileage,
                        "price": car.get("price"),
                        "location": None,  # Not available in JSON, update if you find a field
                        "contact_info": car.get("ownerTitle"),
                        "image_url": image_url,
                        "listing_url": car.get("url")
                    })

            offset += limit

    return all_listings

if __name__ == "__main__":
    listings = get_autotrader_listings()
    for car in listings:
        print(car)
