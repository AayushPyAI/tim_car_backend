from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import app.schemas.craigslist as schemas
import app.crud.craigslist as crud
from scrapers.craigslist.craigslist import get_craigslist_listings

router = APIRouter(prefix="/craigslist", tags=["Craigslist"])

@router.post("/create", response_model=schemas.CraigslistListingOut)
def create(listing: schemas.CraigslistListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, listing)

@router.get("/list", response_model=list[schemas.CraigslistListingOut])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_store(db: Session = Depends(get_db)):
    listings = get_craigslist_listings()
    created = []
    for item in listings:
        try:
            listing_obj = schemas.CraigslistListingCreate(**item)
            created.append(crud.create_listing(db, listing_obj))
        except Exception as e:
            print("Error saving listing:", e)
    return {"saved": len(created), "listings": created}
