from sqlalchemy import Column, Integer, String, Float, Text
from app.database import Base

class OVEListing(Base):
    __tablename__ = "ove_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    price = Column(Float)
    location = Column(String)
    contact_info = Column(Text)
    image_url = Column(Text)
    listing_url = Column(Text)
