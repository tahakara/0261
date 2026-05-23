from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    id: Optional[str] = None
    car_id: str
    lot_id: str
    action: str  # 'entry' veya 'exit'
    timestamp: datetime
