# models/dupont.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class DupontListing(Base):
    __tablename__ = "dupont_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    vin = Column(String)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Float)
    price = Column(Float)
    location = Column(String)
    contact_info = Column(String)
    image_url = Column(String)
    listing_url = Column(String)
    dealer_name = Column(String)
