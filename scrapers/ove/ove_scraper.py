import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

def get_ove_listings():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get("https://www.ove.com/search/results#/results/85e104b4-74e4-4387-b649-1f3c56ec19b0")
    sleep(6)  # Wait for JS-rendered content

    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div[data-cmp="itemCard"]')  # Adjust selector as needed

    for card in cards:
        try:
            title = card.find_element(By.CSS_SELECTOR, 'h2[data-cmp="subheading"]').text
            price = float(card.find_element(By.CSS_SELECTOR, 'div[data-cmp="firstPrice"]').text.replace(",", "").replace("$", ""))
            link = card.find_element(By.CSS_SELECTOR, 'a[data-cmp="link"]').get_attribute("href")
            image_url = card.find_element(By.CSS_SELECTOR, 'img[data-cmp="inventoryImage"]').get_attribute("src")

            listing = {
                "title": title,
                "price": price,
                "location": "Location Placeholder",  # Adjust as necessary
                "contact_info": "Contact Info Placeholder",  # Adjust as necessary
                "image_url": image_url,
                "listing_url": link,
            }
            listings.append(listing)

        except Exception as e:
            print("Error parsing card:", e)

    driver.quit()
    return listings
