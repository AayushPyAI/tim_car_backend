# models/cars.py
from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class CarsDotComListing(Base):
    __tablename__ = "cars_dot_com_listings"

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
    listing_url = Column(String, unique=True)
    dealer_name = Column(String)
