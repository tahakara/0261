from fastapi import APIRouter, HTTPException
from app.models.transaction import Transaction
from app.db.couch import COUCHDB_URL, COUCHDB_DB, get_session

router = APIRouter(prefix="/transactions", tags=["Transactions"])

TRANSACTION_DB = COUCHDB_DB + "_transactions"

@router.get("/", response_model=list[Transaction])
async def list_transactions():
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{TRANSACTION_DB}/_all_docs?include_docs=true") as resp:
            data = await resp.json()
            txs = [Transaction(id=row['doc'].get('_id'), **{k: v for k, v in row['doc'].items() if k not in ['_id', '_rev']}) for row in data.get('rows', [])]
            return txs

@router.post("/", response_model=Transaction)
async def create_transaction(tx: Transaction):
    async with await get_session() as session:
        async with session.post(f"{COUCHDB_URL}{TRANSACTION_DB}", json=tx.dict(exclude_unset=True)) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            result = await resp.json()
            tx.id = result['id']
            return tx
