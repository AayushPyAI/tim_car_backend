# schemas/cargurus.py
from pydantic import BaseModel
from typing import Optional

class CarGurusListingBase(BaseModel):
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
  

class CarGurusListingCreate(CarGurusListingBase):
    pass

class CarGurusListingOut(CarGurusListingBase):
    id: int

    class Config:
        orm_mode = True
