
# routers/cargurus.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
import app.schemas.cargurus as schemas
import app.crud.cargurus as crud
from scrapers.cargurus.cargurus import get_cargurus_listings

router = APIRouter(prefix="/cargurus", tags=["CarGurus"])

@router.post("/create", response_model=schemas.CarGurusListingOut)
def create(listing: schemas.CarGurusListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, listing)

@router.get("/list", response_model=list[schemas.CarGurusListingOut])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_store(db: Session = Depends(get_db)):
    listings = get_cargurus_listings()
    created = []
    for item in listings:
        try:
            listing_obj = schemas.CarGurusListingCreate(**item)
            created.append(crud.create_listing(db, listing_obj))
        except Exception as e:
            print("Error saving listing:", e)
    return {"saved": len(created), "listings": created}

