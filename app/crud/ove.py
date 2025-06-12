from sqlalchemy.orm import Session
from app.models.ove import OVEListing
from app.schemas.ove import OVEListingCreate

def create_listing(db: Session, listing: OVEListingCreate):
    db_listing = OVEListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(OVEListing).offset(skip).limit(limit).all()
