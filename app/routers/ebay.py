from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.ebay import EbayListingCreate, EbayListingOut
from app.crud import ebay as crud_ebay
from scrapers.ebay.ebay_scraper import get_ebay_listings

router = APIRouter(prefix="/api/ebay", tags=["ebay"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/listings/", response_model=EbayListingOut)
def create_ebay_listing(listing: EbayListingCreate, db: Session = Depends(get_db)):
    return crud_ebay.create_listing(db, listing)

@router.get("/listings/", response_model=list[EbayListingOut])
def read_ebay_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_ebay.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_save(db: Session = Depends(get_db)):
    listings = get_ebay_listings()
    results = []
    for item in listings:
        try:
            listing_obj = EbayListingCreate(**item)
            saved = crud_ebay.create_listing(db, listing_obj)
            results.append(saved)
        except Exception as e:
            print("Error saving listing:", e)
    return {"added": len(results), "items": results[:5]}  # just show top 5
