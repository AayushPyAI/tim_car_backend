from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.ove import OVEListingCreate, OVEListingOut
from app.crud import ove as crud_ove
from scrapers.ove.ove_scraper import get_ove_listings

router = APIRouter(prefix="/api/ove", tags=["ove"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/listings/", response_model=OVEListingOut)
def create_ove_listing(listing: OVEListingCreate, db: Session = Depends(get_db)):
    return crud_ove.create_listing(db, listing)

@router.get("/listings/", response_model=list[OVEListingOut])
def read_ove_listings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_ove.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape/")
def scrape_and_save(db: Session = Depends(get_db)):
    listings = get_ove_listings()
    results = []
    for item in listings:
        try:
            listing_obj = OVEListingCreate(**item)
            saved = crud_ove.create_listing(db, listing_obj)
            results.append(saved)
        except Exception as e:
            print("Error saving listing:", e)
    return {"added": len(results), "items": results[:5]}
