# main.py
from fastapi import FastAPI
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ebay, autotrader, cars, cargurus, dupont, craigslist
from app.models import ebay as ebay_model
from app.models import autotrader as autotrader_model
from app.models import cars as cars_model
from app.models import cargurus as cargurus_model
from app.models import dupont as dupoint_model
from app.models import craigslist as craigslist_model

Base.metadata.create_all(bind=engine)

app = FastAPI()


# ✅ Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Or ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(ebay.router)
app.include_router(autotrader.router)
app.include_router(cars.router)
app.include_router(cargurus.router)
app.include_router(dupont.router)
app.include_router(craigslist.router)

