
# schemas/dupont.py
from pydantic import BaseModel
from typing import Optional

class DupontListingBase(BaseModel):
    title: str
    vin: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[float] = None
    price: Optional[float] = None
    location: Optional[str] = None
    contact_info: Optional[str] = None
    image_url: Optional[str] = None
    listing_url: Optional[str] = None
    dealer_name: Optional[str] = None

class DupontListingCreate(DupontListingBase):
    pass

class DupontListingOut(DupontListingBase):
    id: int

    class Config:
        orm_mode = True
