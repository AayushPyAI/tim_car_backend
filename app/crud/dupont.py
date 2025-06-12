# crud/dupont.py
from sqlalchemy.orm import Session
import app.models.dupont as models
import app.schemas.dupont as schemas

def create_listing(db: Session, listing: schemas.DupontListingCreate):
    db_listing = models.DupontListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.DupontListing).offset(skip).limit(limit).all()
