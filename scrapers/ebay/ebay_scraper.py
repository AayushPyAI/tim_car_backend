import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.ebay import EbayListing
from app.database import Base
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
import re
from sqlalchemy import or_

DATABASE_URL = "postgresql://postgres:Java_123@localhost:5432/luxurycars"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_detail_value(driver, label_text=None, class_keyword=None):
    try:
        if class_keyword:
            xpath = f"//dl[contains(@class, 'ux-labels-values--{class_keyword}')]//dd//span"
        else:
            xpath = f"//dl[.//span[normalize-space(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'))='{label_text.lower()}']]//dd//span"
        element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return element.text.strip()
    except Exception as e:
        print(f"Failed to get value for {label_text or class_keyword}: {e}")
        return "N/A"

def scrape_listing_details(driver, url):
    print(f"Scraping: {url}")
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ux-layout-section-module-evo__container"))
        )
        vin = get_detail_value(driver, "VIN (Vehicle Identification Number)")
        year = get_detail_value(driver, "Year")
        make = get_detail_value(driver, class_keyword="make")
        model = get_detail_value(driver, "Model")
        mileage = get_detail_value(driver, "Mileage")
        location_xpath = "//div[contains(@class, 'ux-labels-values-with-hints--SECONDARY-SMALL')]//span[contains(@class, 'ux-textspans--SECONDARY')]"
        location_element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, location_xpath)))
        location = location_element.text.strip() if location_element else "N/A"
        contact_info = "eBay internal message"
        dealer_name = "N/A"
        is_private_seller = True
        return {
            "vin": vin,
            "year": year,
            "make": make,
            "model": model,
            "mileage": mileage,
            "location": location,
            "contact_info": contact_info,
            "dealer_name": dealer_name,
            "is_private_seller": is_private_seller,
        }
    except Exception as e:
        print(f"⚠️ Error parsing item: {e}")
        return {
            "vin": "N/A", "year": "N/A", "make": "N/A", "model": "N/A", "mileage": "N/A",
            "location": "N/A", "contact_info": "eBay internal message", "dealer_name": "N/A", "is_private_seller": True
        }

def extract_ebay_item_number(url):
    match = re.search(r'/itm/(\d+)', url)
    return match.group(1) if match else None

def get_ebay_listings():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    base_url = "https://www.ebay.com/b/Private-Seller-Cars-and-Trucks/6001/bn_55180091?mag=1&Make=ASTON%2520MARTIN%7CFerrari%7CLamborghini%7CMcLaren%7CPorsche%7CRolls%252DRoyce"
    listing_data = []
    for page in range(1, 4):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}&_pgn={page}&rt=nc"
        driver.get(url)
        time.sleep(5)
        raw_items = driver.find_elements(By.CSS_SELECTOR, "li.brwrvr__item-card")
        collected_urls = []
        for item in raw_items:
            try:
                title_elem = item.find_element(By.CSS_SELECTOR, "h3.bsig__title__text")
                price_elem = item.find_element(By.CSS_SELECTOR, "span.bsig__price--displayprice")
                link_elem = item.find_element(By.CSS_SELECTOR, "a.bsig__title__wrapper")
                image_elem = item.find_element(By.CSS_SELECTOR, "img")
                listing_url = link_elem.get_attribute("href")
                item_number = extract_ebay_item_number(listing_url)
                image_urls = []
                for img in item.find_elements(By.CSS_SELECTOR, "img"):
                    src = img.get_attribute("src")
                    data_originalsrc = img.get_attribute("data-originalsrc")
                    if src and src.endswith('.webp'):
                        image_urls.append(src)
                    if data_originalsrc and data_originalsrc.endswith('.webp'):
                        image_urls.append(data_originalsrc)
                image_url = image_urls[0] if image_urls else ''
                collected_urls.append({
                    "title": title_elem.text.strip(),
                    "price": float(price_elem.text.replace('$', '').replace(',', '').strip()),
                    "listing_url": listing_url,
                    "image_url": image_url,
                    "item_number": item_number
                })
            except Exception as e:
                print("⚠️ Error collecting from listing:", e)
                continue
        for item in collected_urls:
            details = scrape_listing_details(driver, item["listing_url"])
            listing = {
                **item,
                "vin": details["vin"],
                "make": details["make"],
                "model": details["model"],
                "year": details["year"],
                "mileage": details["mileage"],
                "location": details["location"],
                "contact_info": details["contact_info"]
            }
            listing_data.append(listing)
    driver.quit()
    return listing_data

def clean_listing(item):
    # Convert year and mileage to int/float or None
    for key in ["year", "mileage", "price"]:
        val = item.get(key)
        if isinstance(val, str):
            if val.strip().upper() == "N/A" or not val.strip():
                item[key] = None
            else:
                try:
                    if key == "year":
                        item[key] = int(val)
                    else:
                        item[key] = float(val)
                except Exception:
                    item[key] = None
    return item

def save_listings_to_db(listings):
    session = SessionLocal()
    for item in listings:
        item = clean_listing(item)
        obj = session.query(EbayListing).filter(
            or_(EbayListing.listing_url == item["listing_url"], EbayListing.item_number == item["item_number"])
        ).first()
        if obj:
            for k, v in item.items():
                setattr(obj, k, v)
        else:
            obj = EbayListing(**item)
            session.add(obj)
    session.commit()
    session.close()
    print(f"[INFO] Saved {len(listings)} eBay listings to DB.")

def scheduled_scrape_and_save():
    print("[INFO] Running scheduled eBay scrape...")
    listings = get_ebay_listings()
    if listings:
        save_listings_to_db(listings)
    else:
        print("[WARN] No eBay listings scraped.")

if __name__ == "__main__":
    if "--manual" in sys.argv:
        print("[INFO] Manual run triggered.")
        scheduled_scrape_and_save()
    else:
        scheduler = BlockingScheduler(timezone="UTC")
        scheduler.add_job(scheduled_scrape_and_save, 'cron', hour=1, minute=0)
        print("[INFO] Scheduler started. eBay scraper will run every day at 01:00 UTC.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("[INFO] Scheduler stopped.")
