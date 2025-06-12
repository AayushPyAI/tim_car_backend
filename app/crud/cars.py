
# crud/cars.py
from sqlalchemy.orm import Session
import app.models.cars as models
import app.schemas.cars as schemas

def create_listing(db: Session, listing: schemas.CarsDotComListingCreate):
    db_listing = models.CarsDotComListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CarsDotComListing).offset(skip).limit(limit).all()
