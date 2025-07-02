from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.autotrader import AutotraderListingCreate, AutotraderListingOut
from app.crud import autotrader as crud_autotrader
from scrapers.autotrader.autotrader_scraper import get_autotrader_listings, fetch_detail_info
from concurrent.futures import ThreadPoolExecutor, as_completed

router = APIRouter(prefix="/api/autotrader", tags=["autotrader"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/listings/", response_model=AutotraderListingOut)
def create_autotrader_listing(listing: AutotraderListingCreate, db: Session = Depends(get_db)):
    return crud_autotrader.create_listing(db, listing)

@router.get("/listings/", response_model=list[AutotraderListingOut])
def read_autotrader_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_autotrader.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_save(db: Session = Depends(get_db)):
    summaries = get_autotrader_listings()
    results = []
    # Fetch details for each listing (parallel for speed)
    detailed = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_listing = {executor.submit(fetch_detail_info, l): l for l in summaries}
        for future in as_completed(future_to_listing):
            detailed.append(future.result())
    for item in detailed:
        try:
            listing_obj = AutotraderListingCreate(**item)
            saved = crud_autotrader.create_listing(db, listing_obj)
            results.append(saved)
        except Exception as e:
            print("Error saving listing:", e)
    return {"added": len(results), "items": results[:5]}
