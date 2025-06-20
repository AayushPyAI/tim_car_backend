from sqlalchemy.orm import Session
from app.models.ebay import EbayListing
from app.schemas.ebay import EbayListingCreate

def create_listing(db: Session, listing: EbayListingCreate):
    existing = db.query(EbayListing).filter(EbayListing.listing_url == listing.listing_url).first()
    if existing:
        return existing
    db_listing = EbayListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EbayListing).offset(skip).limit(limit).all()
