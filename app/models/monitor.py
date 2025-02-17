"""
Database models for the monitoring system.

This module defines SQLAlchemy ORM models for monitors, their states, and tags.
"""

import enum
from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship

from .base import Base


class MonitorState(enum.Enum):
    """Monitor state enumeration."""

    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"
    MISSING_DATA = "Missing Data"


# Association table for many-to-many relationship between Monitors and Tags
monitor_tags = Table(
    "monitor_tags",
    Base.metadata,
    Column(
        "monitor_id",
        Integer,
        ForeignKey("monitors.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Monitor(Base):
    """
    Monitor model representing a system or service being monitored.

    Attributes:
        id: Unique identifier
        name: Monitor name
        states: Relationship to monitor states
        tags: Relationship to monitor tags
    """

    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    states = relationship(
        "MonitorStatus", back_populates="monitor", cascade="all, delete-orphan"
    )
    tags = relationship("Tag", secondary=monitor_tags, back_populates="monitors")


class MonitorStatus(Base):
    """
    Monitor status model representing the state of a monitor at a point in time.

    Attributes:
        id: Unique identifier
        monitor_id: Reference to the monitor
        state: Current state of the monitor
        timestamp: When this state was recorded
        monitor: Relationship to the parent monitor
    """

    __tablename__ = "monitor_statuses"

    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(
        Integer, ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False
    )
    state = Column(Enum(MonitorState), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    monitor = relationship("Monitor", back_populates="states")


class Tag(Base):
    """
    Tag model for categorizing monitors.

    Attributes:
        id: Unique identifier
        name: Tag name
        monitors: Relationship to monitors using this tag
    """

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    monitors = relationship("Monitor", secondary=monitor_tags, back_populates="tags")


# Rest of your model definitions...
