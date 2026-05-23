from fastapi import APIRouter, HTTPException
from app.models.car import Car
from app.db.couch import COUCHDB_URL, COUCHDB_DB, get_session

router = APIRouter(prefix="/cars", tags=["Cars"])

CAR_DB = COUCHDB_DB + "_cars"

@router.get("/", response_model=list[Car])
async def list_cars():
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{CAR_DB}/_all_docs?include_docs=true") as resp:
            data = await resp.json()
            cars = [Car(id=row['doc'].get('_id'), **{k: v for k, v in row['doc'].items() if k not in ['_id', '_rev']}) for row in data.get('rows', [])]
            return cars

@router.post("/", response_model=Car)
async def create_car(car: Car):
    async with await get_session() as session:
        async with session.post(f"{COUCHDB_URL}{CAR_DB}", json=car.dict(exclude_unset=True)) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            result = await resp.json()
            car.id = result['id']
            return car

@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: str):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{CAR_DB}/{car_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            data = await resp.json()
            return Car(id=data['_id'], **{k: v for k, v in data.items() if k not in ['_id', '_rev']})

@router.put("/{car_id}", response_model=Car)
async def update_car(car_id: str, car: Car):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{CAR_DB}/{car_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        data = car.dict(exclude_unset=True)
        data['_rev'] = current['_rev']
        async with session.put(f"{COUCHDB_URL}{CAR_DB}/{car_id}", json=data) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return Car(id=car_id, **{k: v for k, v in data.items() if k != '_rev'})

@router.delete("/{car_id}")
async def delete_car(car_id: str):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{CAR_DB}/{car_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        async with session.delete(f"{COUCHDB_URL}{CAR_DB}/{car_id}?rev={current['_rev']}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return {"ok": True}
