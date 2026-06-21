import uuid
from typing import Optional

from pydantic import BaseModel

class CompanyOut(BaseModel):
    id: uuid.UUID
    symbol: str
    trading_symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    is_benchmark: bool

    model_config = {"from_attributes": True}

class UniverseStats(BaseModel):
    total_companies: int
    total_price_rows: int
    total_fundamental_rows: int
    earliest_price_date: Optional[str] = None
    latest_price_date: Optional[str] = None
    sectors: list[str] = []
