import requests
import json
import re

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

def get_cargurus_listings(
    dataset_ids=None,
    token=None
):
    if dataset_ids is None:
        dataset_ids = [
            "rkJNryuM85XUl3jdp",  # Audi
            "yMtcdtrSdHeTQ9GW9", #volkswagen
            "KwTq6qBGJJo0S1xIx", #ferrari
            "qrty7bCPaAiAHsO61", #lamborghini
            "g7dmrXqlWQ1otBo2q", #porsche
            "Bv2fSawj65PnBeR4Y", #bentley
            "V2dqRKoaCezP0ztUL", #toyota

          
           
        ]
    if token is None:
        token = "apify_api_6KK0g25uue0hau5wcDnrI1P0H1sXcX0gVfpi"

    all_listings = []

    for dataset_id in dataset_ids:
        logging.info(f"\n🔍 Fetching data for dataset: {dataset_id}")
        base_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
        limit = 100
        offset = 0

        while True:
            url = f"{base_url}?format=json&clean=true&token={token}&limit={limit}&offset={offset}"
            response = requests.get(url, headers={"Accept": "application/json"})

            try:
                data = response.json()
            except json.JSONDecodeError as e:
                logging.error(f"JSON Decode Error in dataset {dataset_id}: {e}")
                break

            if not data:
                break

            for car in data:
                if isinstance(car, dict):
                    title = car.get("name", "")
                    year, make, model = extract_car_details(title)
                    description = car.get("description", "")
                    mileage = extract_mileage(description)
                    location = extract_location(car.get("url", ""))

                    all_listings.append({
                        "title": title,
                        "vin": car.get("id"),
                        "make": make,
                        "model": model,
                        "year": year,
                        "mileage": mileage,
                        "price": car.get("price"),
                        "location": location,
                        "contact_info": None,
                        "image_url": car.get("primaryImage"),
                        "listing_url": car.get("url")
                    })

            offset += limit

    return all_listings

# if __name__ == "__main__":
#     listings = get_cargurus_listings()
#     for car in listings:
#         logging.info(f"Title: {car.get('title')}")
#         logging.info(f"VIN: {car.get('vin')}")
#         logging.info(f"Make: {car.get('make')}")
#         logging.info(f"Model: {car.get('model')}")
#         logging.info(f"Year: {car.get('year')}")
#         logging.info(f"Mileage: {car.get('mileage')}")
#         logging.info(f"Price: {car.get('price')}")
#         logging.info(f"Location: {car.get('location')}")
#         logging.info(f"Contact Info: {car.get('contact_info')}")
#         logging.info(f"Image URL: {car.get('image_url')}")
#         logging.info(f"Listing URL: {car.get('listing_url')}")
#         logging.info("-" * 60)
