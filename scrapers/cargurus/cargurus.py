import requests
import json
import re

def extract_car_details(title):
    # Common pattern: YEAR MAKE MODEL
    pattern = r'(\d{4})\s+([A-Za-z]+)\s+([A-Za-z0-9\s-]+)'
    match = re.match(pattern, title)
    if match:
        year = match.group(1)
        make = match.group(2)
        model = match.group(3).strip()
        return year, make, model
    return None, None, None

def extract_mileage(description):
    # Pattern to match mileage in description
    pattern = r'(\d{1,3}(?:,\d{3})*)\s*mi'
    match = re.search(pattern, description)
    if match:
        return match.group(1).replace(',', '')
    return None

def extract_location(url):
    # Extract zip code from URL
    pattern = r'zip=(\d{5})'
    match = re.search(pattern, url)
    if match:
        return f"Zip: {match.group(1)}"
    return None

def get_cargurus_listings():
    dataset_id = "ilDsh48oVLueUeYfk"
    token = "apify_api_6KK0g25uue0hau5wcDnrI1P0H1sXcX0gVfpi"
    # Replace with your real token

    url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?format=json&clean=true&token={token}"

    response = requests.get(url, headers={"Accept": "application/json"})

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)
        return []

    processed_listings = []
    for car in data:
        if isinstance(car, dict):
            title = car.get("name", "")
            year, make, model = extract_car_details(title)
            description = car.get("description", "")
            mileage = extract_mileage(description)
            location = extract_location(car.get("url", ""))
            
            processed_listings.append({
                "title": title,
                "vin": car.get("id"),
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": car.get("price"),
                "location": location,
                "contact_info": None,  # This would require scraping individual listing pages
                "image_url": car.get("primaryImage"),
                "listing_url": car.get("url")
            })
    
    return processed_listings

# if __name__ == "__main__":
#     # For testing the scraper directly
#     listings = get_cargurus_listings()
#     for car in listings:
#         print("Title:", car.get("title"))
#         print("VIN:", car.get("vin"))
#         print("Make:", car.get("make"))
#         print("Model:", car.get("model"))
#         print("Year:", car.get("year"))
#         print("Mileage:", car.get("mileage"))
#         print("Price:", car.get("price"))
#         print("Location:", car.get("location"))
#         print("Contact Info:", car.get("contact_info"))
#         print("Image URL:", car.get("image_url"))
#         print("Listing URL:", car.get("listing_url"))
#         print("-" * 60)
