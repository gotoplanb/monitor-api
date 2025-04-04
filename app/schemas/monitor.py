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

    id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class MonitorStatusUpdate(BaseModel):
    """Schema for updating Monitor status."""

    state: MonitorState
    message: str | None = None

    model_config = ConfigDict(from_attributes=True)


class MonitorStatusResponse(BaseModel):
    """Schema for Monitor status response."""

    id: int
    name: str
    state: MonitorState
    message: str | None = None
    timestamp: datetime
    tags: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class MonitorResponse(MonitorBase):
    """Schema for Monitor response."""

    id: int
    tags: List[str]

    model_config = ConfigDict(from_attributes=True)
