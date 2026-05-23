from pydantic import BaseModel
from typing import Optional

class ParkingLot(BaseModel):
    id: Optional[str] = None
    name: str
    capacity: int
    occupied: int = 0
    location: Optional[str] = None
