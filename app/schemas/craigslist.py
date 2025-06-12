from pydantic import BaseModel
from typing import Optional

class CraigslistListingBase(BaseModel):
    title: str
    vin: Optional[str] = "N/A"
    make: Optional[str] = "Unknown"
    model: Optional[str] = "Unknown"
    year: Optional[int] = 2020
    mileage: Optional[float] = 0.0
    price: float
    location: Optional[str] = "N/A"
    contact_info: Optional[str] = "N/A"
    image_url: Optional[str] = ""
    listing_url: str
    dealer_name: Optional[str] = "N/A"

class CraigslistListingCreate(CraigslistListingBase):
    pass

class CraigslistListingOut(CraigslistListingBase):
    id: int

    class Config:
        orm_mode = True
