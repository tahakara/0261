from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.db.couch import COUCHDB_URL, COUCHDB_DB, get_session

router = APIRouter(prefix="/users", tags=["Users"])

USER_DB = COUCHDB_DB + "_users"

@router.get("/", response_model=list[User])
async def list_users():
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{USER_DB}/_all_docs?include_docs=true") as resp:
            data = await resp.json()
            users = [User(id=row['doc'].get('_id'), **{k: v for k, v in row['doc'].items() if k not in ['_id', '_rev']}) for row in data.get('rows', [])]
            return users

@router.post("/", response_model=User)
async def create_user(user: User):
    async with await get_session() as session:
        async with session.post(f"{COUCHDB_URL}{USER_DB}", json=user.dict(exclude_unset=True)) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            result = await resp.json()
            user.id = result['id']
            return user

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{USER_DB}/{user_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            data = await resp.json()
            return User(id=data['_id'], **{k: v for k, v in data.items() if k not in ['_id', '_rev']})

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{USER_DB}/{user_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        data = user.dict(exclude_unset=True)
        data['_rev'] = current['_rev']
        async with session.put(f"{COUCHDB_URL}{USER_DB}/{user_id}", json=data) as resp:
            if resp.status != 201:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return User(id=user_id, **{k: v for k, v in data.items() if k != '_rev'})

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    async with await get_session() as session:
        async with session.get(f"{COUCHDB_URL}{USER_DB}/{user_id}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            current = await resp.json()
        async with session.delete(f"{COUCHDB_URL}{USER_DB}/{user_id}?rev={current['_rev']}") as resp:
            if resp.status != 200:
                raise HTTPException(status_code=resp.status, detail=await resp.text())
            return {"ok": True}
