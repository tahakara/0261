from fastapi import APIRouter, HTTPException
from app.models.parking_lot import ParkingLot
from app.db.couch import COUCHDB_URL, COUCHDB_DB, get_session

router = APIRouter(prefix="/parking-lots", tags=["Parking Lots"])

@router.get("/", response_model=list[ParkingLot])
async def list_parking_lots():
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{COUCHDB_DB}/_all_docs?include_docs=true") as resp:
            data = await resp.json()
            lots = [ParkingLot(id=row['doc'].get('_id'), **{k: v for k, v in row['doc'].items() if k not in ['_id', '_rev']}) for row in data.get('rows', [])]
            return lots

@router.post("/", response_model=ParkingLot)
async def create_parking_lot(lot: ParkingLot):
    async with await get_session() as session:
        async with session.post(f"{COUCHDB_URL}{COUCHDB_DB}", json=lot.dict(exclude_unset=True)) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            result = await resp.json()
            lot.id = result['id']
            return lot

@router.get("/{lot_id}", response_model=ParkingLot)
async def get_parking_lot(lot_id: str):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{COUCHDB_DB}/{lot_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            data = await resp.json()
            return ParkingLot(id=data['_id'], **{k: v for k, v in data.items() if k not in ['_id', '_rev']})

@router.put("/{lot_id}", response_model=ParkingLot)
async def update_parking_lot(lot_id: str, lot: ParkingLot):
    async with await get_session() as session:
        # Get current revision
        async with session.get(f"{COUCHDB_URL}{COUCHDB_DB}/{lot_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        data = lot.dict(exclude_unset=True)
        data['_rev'] = current['_rev']
        async with session.put(f"{COUCHDB_URL}{COUCHDB_DB}/{lot_id}", json=data) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return ParkingLot(id=lot_id, **{k: v for k, v in data.items() if k != '_rev'})

@router.delete("/{lot_id}")
async def delete_parking_lot(lot_id: str):
    async with await get_session() as session:
        # Get current revision
        async with session.get(f"{COUCHDB_URL}{COUCHDB_DB}/{lot_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        async with session.delete(f"{COUCHDB_URL}{COUCHDB_DB}/{lot_id}?rev={current['_rev']}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return {"ok": True}
