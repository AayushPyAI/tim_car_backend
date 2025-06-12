
# crud/cargurus.py
from sqlalchemy.orm import Session
import app.models.cargurus as models
import app.schemas.cargurus as schemas

def create_listing(db: Session, listing: schemas.CarGurusListingCreate):
    db_listing = models.CarGurusListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.CarGurusListing).offset(skip).limit(limit).all()
