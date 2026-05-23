import os
from dotenv import load_dotenv
import aiohttp

load_dotenv()

COUCHDB_URL = os.getenv("COUCHDB_URL")
COUCHDB_USER = os.getenv("COUCHDB_USER")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD")
COUCHDB_DB = os.getenv("COUCHDB_DB")

async def get_session():
    return aiohttp.ClientSession(auth=aiohttp.BasicAuth(COUCHDB_USER, COUCHDB_PASSWORD))
