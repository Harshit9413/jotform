from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from datetime import datetime


class IntegrationCreate(BaseModel):
    form_id: str
    type: str
    config: Dict[str, Any]


class IntegrationOut(BaseModel):
    id: int
    form_id: str
    type: str
    config: Dict[str, Any]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class IntegrationLogOut(BaseModel):
    id: int
    integration_id: int
    submission_id: int
    status: str
    error_message: Optional[str] = None
    triggered_at: datetime

    class Config:
        from_attributes = True
