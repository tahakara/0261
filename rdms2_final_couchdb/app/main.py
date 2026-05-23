
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import parking_lot, car, user, transaction
import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

app = FastAPI(title="Otopark Yönetim Sistemi")

# Parking lot router'ı ekle

app.include_router(parking_lot.router)
app.include_router(car.router)
app.include_router(user.router)
app.include_router(transaction.router)

# Statik dosyaları sun (web arayüzü)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# Dummy data ile ilk başlatma
@app.on_event("startup")
async def startup_event():
    from app.db.init_db import init_dummy_data
    await init_dummy_data()
