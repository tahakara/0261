import os
import aiohttp
from .couch import COUCHDB_URL, COUCHDB_DB, get_session


DUMMY_LOTS = [
    {"name": "Merkez Otoparkı", "capacity": 100, "occupied": 0, "location": "Şehir Merkezi"},
    {"name": "AVM Açık Alan", "capacity": 60, "occupied": 0, "location": "AVM Yanı"},
    {"name": "Kapalı Otopark", "capacity": 80, "occupied": 0, "location": "B1 Katı"},
    {"name": "Hastane Otoparkı", "capacity": 40, "occupied": 0, "location": "Hastane Girişi"},
]
DUMMY_CARS = [
    {"plate": "34ABC123", "brand": "Renault", "model": "Clio", "color": "Beyaz", "owner": "Ali Veli", "lot_id": None},
    {"plate": "06DEF456", "brand": "Ford", "model": "Focus", "color": "Mavi", "owner": "Ayşe Yılmaz", "lot_id": None},
    {"plate": "35GHJ789", "brand": "Toyota", "model": "Corolla", "color": "Gri", "owner": "Mehmet Can", "lot_id": None},
    {"plate": "16XYZ321", "brand": "Fiat", "model": "Egea", "color": "Kırmızı", "owner": "Zeynep Demir", "lot_id": None},
]
# Sadece 1 admin, kullanıcı ekleme yok
DUMMY_USERS = [
    {"username": "admin", "password": "admin123", "is_admin": True},
]
DUMMY_TRANSACTIONS = []

async def init_dummy_data():
    async with await get_session() as session:
        dbs = [
            COUCHDB_DB,
            COUCHDB_DB + "_cars",
            COUCHDB_DB + "_users",
            COUCHDB_DB + "_transactions"
        ]
        # Önce tüm ilgili veritabanlarını sil
        for db in dbs:
            await session.delete(f"{COUCHDB_URL}{db}")
        # Sonra tekrar oluştur ve dummy data ekle
        # Parking lot DB
        await session.put(f"{COUCHDB_URL}{COUCHDB_DB}")
        for lot in DUMMY_LOTS:
            await session.post(f"{COUCHDB_URL}{COUCHDB_DB}", json=lot)

        # Car DB
        car_db = COUCHDB_DB + "_cars"
        await session.put(f"{COUCHDB_URL}{car_db}")
        for car in DUMMY_CARS:
            await session.post(f"{COUCHDB_URL}{car_db}", json=car)

        # User DB
        user_db = COUCHDB_DB + "_users"
        await session.put(f"{COUCHDB_URL}{user_db}")
        for user in DUMMY_USERS:
            await session.post(f"{COUCHDB_URL}{user_db}", json=user)

        # Transaction DB
        tx_db = COUCHDB_DB + "_transactions"
        await session.put(f"{COUCHDB_URL}{tx_db}")
        for tx in DUMMY_TRANSACTIONS:
            await session.post(f"{COUCHDB_URL}{tx_db}", json=tx)
