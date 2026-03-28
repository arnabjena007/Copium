from pydantic import BaseModel
from typing import Optional

class CostAnomaly(BaseModel):
    id: Optional[str] = None
    timestamp: str
    service: str
    region: str
    resource_id: str
    team: str
    environment: str
    project: str
    cost_usd: float
    cpu_usage_pct: float
    is_anomaly: bool
    severity: str

class IdleResource(BaseModel):
    id: str
    service: str
    resource: str
    owner: str
    wasted_cost: float
    days_idle: int
