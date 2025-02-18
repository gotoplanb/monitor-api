"""
Pydantic schemas for the monitoring system.

This module defines the data validation and serialization schemas using Pydantic.
"""

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from app.models.monitor import MonitorState


class MonitorBase(BaseModel):
    """Base schema for Monitor."""

    name: str
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class MonitorCreate(MonitorBase):
    """Schema for creating a Monitor."""

    model_config = ConfigDict(from_attributes=True)


class MonitorStatusUpdate(BaseModel):
    """Schema for updating Monitor status."""

    state: MonitorState

    model_config = ConfigDict(from_attributes=True)


class MonitorStatusResponse(BaseModel):
    """Schema for Monitor status response."""

    name: str
    state: MonitorState
    timestamp: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class MonitorResponse(MonitorBase):
    """Schema for Monitor response."""

    id: int
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)
