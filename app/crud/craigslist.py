from sqlalchemy.orm import Session
from app.models.craigslist import CraigslistListing
from app.schemas.craigslist import CraigslistListingCreate

def create_listing(db: Session, listing: CraigslistListingCreate):
    db_listing = CraigslistListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CraigslistListing).offset(skip).limit(limit).all()

