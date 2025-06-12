from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
import app.schemas.cars as schemas
import app.crud.cars as crud
from scrapers.cars.cars import get_cars_dot_com_listings

router = APIRouter(prefix="/cars", tags=["Cars.com"])

@router.post("/create", response_model=schemas.CarsDotComListingOut)
def create(listing: schemas.CarsDotComListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, listing)

@router.get("/list", response_model=list[schemas.CarsDotComListingOut])
def list_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_listings(db, skip=skip, limit=limit)

@router.post("/scrape")
def scrape_and_store(db: Session = Depends(get_db)):
    listings = get_cars_dot_com_listings()
    created = []
    for item in listings:
        try:
            listing_obj = schemas.CarsDotComListingCreate(**item)
            created.append(crud.create_listing(db, listing_obj))
        except Exception as e:
            print("Error saving listing:", e)
    return {"saved": len(created), "listings": created}
