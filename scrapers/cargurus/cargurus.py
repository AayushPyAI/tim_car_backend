# scrapers/cargurus/cargurus.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

def get_cargurus_listings():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Use the new URL with search parameters
    url = "https://www.cargurus.com/Cars/inventorylisting/viewDetailsFilterViewInventoryListing.action?sellerHierarchyTypes=PAYING_DEALER&searchId=40d7f03f-3b69-4084-a311-a2da607627de&zip=75093&distance=50&entitySelectingHelper.selectedEntity=m25&sourceContext=carGurusHomePageModel&sortDir=ASC&sortType=BEST_MATCH&srpVariation=DEFAULT_SEARCH&isDeliveryEnabled=true&nonShippableBaseline=0&makeModelTrimPaths=m25&makeModelTrimPaths=m40&makeModelTrimPaths=m48&makeModelTrimPaths=m34&makeModelTrimPaths=m141&makeModelTrimPaths=m121&makeModelTrimPaths=m49&makeModelTrimPaths=m39&makeModelTrimPaths=m129&makeModelTrimPaths=m48%2Fd404&makeModelTrimPaths=m48%2Fd2430&makeModelTrimPaths=m48%2Fd2416&makeModelTrimPaths=m19&makeModelTrimPaths=m19%2Fd1019&makeModelTrimPaths=m19%2Fd2230&makeModelTrimPaths=m20"
    
    driver.get(url)
    sleep(6)

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.inventory-listing')

    for card in cards:
        try:
            title_elem = card.find_elements(By.CSS_SELECTOR, 'h4')
            price_elem = card.find_elements(By.CSS_SELECTOR, 'span[data-test="vehicleCardPricingBlockPrice"]')
            link_elem = card.find_elements(By.CSS_SELECTOR, 'a')
            image_elem = card.find_elements(By.CSS_SELECTOR, 'img')

            title = title_elem[0].text if title_elem else "N/A"
            price = price_elem[0].text.replace("$", "").replace(",", "") if price_elem else "0"
            url = link_elem[0].get_attribute("href") if link_elem else ""
            image_url = image_elem[0].get_attribute("src") if image_elem else ""

            # The VIN, make, model, year, mileage, location, and contact info will be extracted as well.
            # You'll need to update the selectors based on the actual page structure.

            vin = "N/A"  # Modify selector if needed
            make = "Unknown"  # Modify selector if needed
            model = "Unknown"  # Modify selector if needed
            year = 2020  # Modify selector if needed
            mileage = 0.0  # Modify selector if needed
            location = "N/A"  # Modify selector if needed
            contact_info = "CarGurus Internal"  # Modify selector if needed

            listing = {
                "title": title,
                "vin": vin,
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": float(price),
                "location": location,
                "contact_info": contact_info,
                "image_url": image_url,
                "listing_url": url,
                "dealer_name": "N/A"
            }
            listings.append(listing)
        except Exception as e:
            print("Error parsing listing:", e)

    driver.quit()
    return listings

if __name__ == "__main__":
    data = get_cargurus_listings()
    for d in data[:10]:
        print(d)
