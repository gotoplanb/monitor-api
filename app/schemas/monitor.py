"""
Pydantic schemas for the monitoring system.

This module defines the data validation and serialization schemas using Pydantic.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel

from app.models.monitor import MonitorState


class MonitorCreate(BaseModel):
    """Schema for creating a new monitor."""
    name: str
    tags: List[str] = []


class MonitorStatusUpdate(BaseModel):
    """Schema for updating a monitor's state."""
    state: MonitorState


class MonitorStatusResponse(BaseModel):
    """Schema for monitor status response."""
    name: str
    state: MonitorState
    timestamp: datetime
    tags: List[str]

    class Config:
        """Pydantic configuration."""
        from_attributes = True
