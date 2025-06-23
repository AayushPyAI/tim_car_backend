# routers/dupont.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import app.schemas.dupont as schemas
import app.crud.dupont as crud
from scrapers.dupont.dupont import get_dupont_listings

router = APIRouter(prefix="/api/dupont", tags=["Dupont Registry"])

@router.post("/create", response_model=schemas.DupontListingOut)
def create(listing: schemas.DupontListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, listing)

@router.get("/list", response_model=list[schemas.DupontListingOut])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_store(db: Session = Depends(get_db)):
    listings = get_dupont_listings()
    created = []
    for item in listings:
        try:
            listing_obj = schemas.DupontListingCreate(**item)
            created.append(crud.create_listing(db, listing_obj))
        except Exception as e:
            print("Error saving listing:", e)
    return {"saved": len(created), "listings": created}

