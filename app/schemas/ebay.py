from pydantic import BaseModel
from typing import Optional

class EbayListingCreate(BaseModel):
    title: str
    vin: str
    make: str
    model: str
    year: int
    mileage: float
    price: float
    location: str
    contact_info: str
    image_url: str
    listing_url: str
    item_number: Optional[str] = None
    # seller_rating: Optional[str] = None  # ebay-specific

class EbayListingOut(BaseModel):
    id: int
    title: str
    vin: str
    make: str
    model: str
    year: Optional[int] = None
    mileage: Optional[float] = None
    price: Optional[float] = None
    location: str
    contact_info: str
    image_url: str
    listing_url: str
    item_number: str

    class Config:
        orm_mode = True
