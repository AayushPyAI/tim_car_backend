
# schemas/cars.py
from pydantic import BaseModel
from typing import Optional

class CarsDotComListingBase(BaseModel):
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

class CarsDotComListingCreate(CarsDotComListingBase):
    pass

class CarsDotComListingOut(CarsDotComListingBase):
    id: int

    class Config:
        orm_mode = True
