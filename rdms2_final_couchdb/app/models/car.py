from pydantic import BaseModel
from typing import Optional

class Car(BaseModel):
    id: Optional[str] = None
    plate: str
    brand: str
    model: str
    color: str
    owner: Optional[str] = None
    lot_id: Optional[str] = None  # Hangi otoparkta
