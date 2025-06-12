from pydantic import BaseModel
from typing import Optional

class AutotraderListingCreate(BaseModel):
    title: Optional[str]
    vin: Optional[str]
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    mileage: Optional[float]
    price: Optional[float]
    location: Optional[str]
    contact_info: Optional[str]
    image_url: Optional[str]
    listing_url: Optional[str]


class AutotraderListingOut(AutotraderListingCreate):
    id: int

    class Config:
        orm_mode = True
