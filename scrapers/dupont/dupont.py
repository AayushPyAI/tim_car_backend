import os
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.dupont import DupontListing
from app.database import Base
from selenium import webdriver
from selenium.webdriver.chrome.options import Options   
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys

DATABASE_URL = "postgresql://postgres:Java_123@localhost:5432/luxurycars"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Ensure table exists
Base.metadata.create_all(bind=engine)

def save_listings_to_db(listings):
    session = SessionLocal()
    for item in listings:
        # Upsert logic: update if listing_url exists, else insert
        obj = session.query(DupontListing).filter_by(listing_url=item["listing_url"]).first()
        if obj:
            for k, v in item.items():
                setattr(obj, k, v)
        else:
            obj = DupontListing(**item)
            session.add(obj)
    session.commit()
    session.close()
    print(f"[INFO] Saved {len(listings)} listings to DB.")

def scheduled_scrape_and_save():
    print("[INFO] Running scheduled DuPont scrape...")
    listings = get_dupont_listings()
    if listings:
        save_listings_to_db(listings)
    else:
        print("[WARN] No listings scraped.")

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

    brand_urls = [
        ("lamborghini", "https://www.dupontregistry.com/autos/results/lamborghini/all/private"),
        ("ferrari", "https://www.dupontregistry.com/autos/results/ferrari/all/private/filter:page_end=2&page_start=1"),
        ("aston martin", "https://www.dupontregistry.com/autos/results/aston--martin/all/private"),
        ("bentley", "https://www.dupontregistry.com/autos/results/bentley/all/private"),
        ("mclaren", "https://www.dupontregistry.com/autos/results/mclaren/all/private"),
        ("porsche", "https://www.dupontregistry.com/autos/results/porsche/all/private"),
        ("rolls royce", "https://www.dupontregistry.com/autos/results/rolls-royce/all/private"),
    ]

    all_listings = []

    for brand, url in brand_urls:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 30)
            # Wait for the heading to ensure the page is loaded
            wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='autosTitle']")))
            # Find the correct container for car cards
            autos_container = driver.find_element(
                By.XPATH,
                "//div[@id='autosTitle']/following-sibling::div[@data-test='Autos']"
            )
            cards = autos_container.find_elements(By.CSS_SELECTOR, 'div.LilCards-module_product_wrapper__FkNih')
        except Exception as e:
            print(f"Error loading page or finding cards for {brand}:", e)
            continue

        for card in cards:
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, 'h2 a')
                title = title_elem.text.strip()

                price_text = card.find_element(By.CSS_SELECTOR, 'h3 span[data-test="price"]').text.strip()
                try:
                    price = float(price_text.replace(",", ""))
                except:
                    price = 0.0

                # Robust image extraction: get src from img inside the nested structure
                sleep(1)  # Give time for lazy-loaded images
                # Scroll card into view to trigger lazy loading
                driver.execute_script("arguments[0].scrollIntoView();", card)
                sleep(1)  # Wait for image to load

                image_url = None
                try:
                    img_elem = card.find_element(By.CSS_SELECTOR, 'div.LilCards-module_img_container__YTuaW a div.CardSlider-module_img_container__PgVf- img')
                    src = img_elem.get_attribute('src')
                    if src and src.startswith('http'):
                        image_url = src
                        print(f"[DEBUG] Found image in src for card: {title}, url: {src}")
                    else:
                        print(f"[DEBUG] After scroll, image src is missing or not http for card: {title}, src: {src}")
                except Exception as e:
                    print(f"[DEBUG] Could not find image for card: {title} after scroll, error: {e}")
                    image_url = None

                relative_url = title_elem.get_attribute("href")
                listing_url = urljoin("https://www.dupontregistry.com", relative_url)

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

                listing = {
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
                    "listing_url": listing_url,
                    "brand": brand
                }
                all_listings.append(listing)

            except Exception as e:
                print(f"Error parsing listing for {brand}:", e)
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

    driver.quit()
    return all_listings

if __name__ == "__main__":
    if "--manual" in sys.argv:
        print("[INFO] Manual run triggered.")
        scheduled_scrape_and_save()
    else:
        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_job(scheduled_scrape_and_save, 'cron', hour=0, minute=0)
        print("[INFO] Scheduler started. Scraper will run every day at 00:00 UTC.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("[INFO] Scheduler stopped.")

#PYTHONPATH=. python scrapers/dupont/dupont.py --manual
#Scheduled Run : PYTHONPATH=. nohup python -u scrapers/dupont/dupont.py > dupont_nohup.log 2>&1 &





