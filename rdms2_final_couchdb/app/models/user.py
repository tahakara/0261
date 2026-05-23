from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[str] = None
    username: str
    password: str  # Hashlenmiş olmalı (örnek için düz yazıldı)
    is_admin: bool = False
