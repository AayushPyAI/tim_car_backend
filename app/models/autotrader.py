from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class AutotraderListing(Base):
    __tablename__ = "autotrader_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    vin = Column(String, index=True)
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    mileage = Column(Float)
    price = Column(Float)
    location = Column(String)
    contact_info = Column(Text)
    image_url = Column(Text)
    listing_url = Column(Text)
