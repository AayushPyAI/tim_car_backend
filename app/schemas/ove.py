from pydantic import BaseModel
from typing import Optional

class OVEListingCreate(BaseModel):
    title: str
    price: float
    location: str
    contact_info: str
    image_url: str
    listing_url: str

class OVEListingOut(OVEListingCreate):
    id: int

    class Config:
        orm_mode = True
