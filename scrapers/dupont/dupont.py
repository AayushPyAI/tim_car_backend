from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_dupont_listings():
    chrome_options = Options()
    
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(180)

    try:
        driver.get("https://www.dupontregistry.com/autos/results/all/all/private/filter:categories=exotic")
        # Wait for the cards to load
        wait = WebDriverWait(driver, 30)
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.LilCards-module_product_wrapper__FkNih')))
       
    except Exception as e:
        print("Error loading page or finding cards:", e)
        driver.quit()
        return []


    listings = []
    cards = driver.find_elements(By.CSS_SELECTOR, 'div.LilCards-module_product_wrapper__FkNih')

    for card in cards:  # Limiting to first 10 for speed; increase if needed
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, 'h2 a')
            title = title_elem.text.strip()

            price_text = card.find_element(By.CSS_SELECTOR, 'h3 span[data-test="price"]').text.strip()
            try:
                price = float(price_text.replace(",", ""))
            except:
                price = 0.0

            image_elem = card.find_element(By.CSS_SELECTOR, 'img')
            image_url = image_elem.get_attribute("src")

            relative_url = title_elem.get_attribute("href")
            listing_url = urljoin("https://www.dupontregistry.com", relative_url)

            # Visit listing URL to get VIN and details
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(listing_url)
            sleep(3)

            try:
                vin = driver.find_element(By.CSS_SELECTOR, '[data-test="VIN"] .AvatarWithTitle_info_text__C_POD').text.strip()
            except:
                vin = "N/A"

            try:
                year_model_make = title.split(" ", 2)
                year = int(year_model_make[0])
                make = year_model_make[1]
                model = year_model_make[2] if len(year_model_make) > 2 else "Unknown"
            except:
                year, make, model = 2020, "Unknown", "Unknown"

            try:
                mileage_elem = driver.find_element(By.CSS_SELECTOR, '[data-test="Mileage"] [itemprop="mileageFromOdometer"]')
                mileage_text = mileage_elem.text.strip().replace(",", "").replace(" miles", "").replace(" mi", "")
                mileage = float(mileage_text)

            except:
                mileage = 0.0

            try:
                contact_elem = driver.find_element(By.CSS_SELECTOR, 'a[href^="tel:"]')
                contact_info = contact_elem.get_attribute("href").replace("tel:", "").strip()
            except:
                contact_info = "N/A"


            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            listings.append({
                "title": title,
                "vin": vin,
                "make": make,
                "model": model,
                "year": year,
                "mileage": mileage,
                "price": price,
                "location": "N/A",
                "contact_info": contact_info,
                "image_url": image_url,
                "listing_url": listing_url
        
            })

        except Exception as e:
            print("Error parsing listing:", e)
            if len(driver.window_handles) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    return listings

if __name__ == "__main__":
    data = get_dupont_listings()
    for d in data:
        print(d)






