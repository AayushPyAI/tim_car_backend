from sqlalchemy.orm import Session
from app.models.autotrader import AutotraderListing
from app.schemas.autotrader import AutotraderListingCreate

def create_listing(db: Session, listing: AutotraderListingCreate):
    existing = db.query(AutotraderListing).filter(AutotraderListing.listing_url == listing.listing_url).first()
    if existing:
        return existing
    db_listing = AutotraderListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(AutotraderListing).offset(skip).limit(limit).all()
