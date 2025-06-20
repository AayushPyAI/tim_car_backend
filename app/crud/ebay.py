from sqlalchemy.orm import Session
from app.models.ebay import EbayListing
from app.schemas.ebay import EbayListingCreate

def create_listing(db: Session, listing: EbayListingCreate):
    # Prefer duplicate check by item_number if present
    if hasattr(listing, 'item_number') and listing.item_number:
        existing = db.query(EbayListing).filter(EbayListing.item_number == listing.item_number).first()
    else:
        existing = db.query(EbayListing).filter(EbayListing.listing_url == listing.listing_url).first()
    if existing:
        # Only update the price if it has changed
        if existing.price != listing.price:
            existing.price = listing.price
            db.commit()
            db.refresh(existing)
        return existing
    db_listing = EbayListing(**listing.dict())
    db.add(db_listing)
    db.commit()
    db.refresh(db_listing)
    return db_listing

def get_listings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(EbayListing).offset(skip).limit(limit).all()
