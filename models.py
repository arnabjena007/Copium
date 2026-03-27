from pydantic import BaseModel
from typing import Optional

class CostAnomaly(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    service: str
    resource: str
    owner: str
    reason: str
    cost_original: float
    cost_optimized: float
    anomaly_score: float
    wasted_cost: float = 0.0

class IdleResource(BaseModel):
    id: str
    service: str
    resource: str
    owner: str
    wasted_cost: float
    days_idle: int
