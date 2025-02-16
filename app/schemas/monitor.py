from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.models.monitor import MonitorState

class MonitorCreate(BaseModel):
    name: str
    tags: List[str] = []

class MonitorStatusUpdate(BaseModel):
    state: MonitorState

class MonitorStatusResponse(BaseModel):
    name: str
    state: MonitorState
    timestamp: datetime
    tags: List[str]

    class Config:
        from_attributes = True 