"""
Database models for the monitoring system.

This module defines SQLAlchemy ORM models for monitors, their states, and tags.
"""

from datetime import UTC, datetime
import enum

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship

from app.models.base import Base


class MonitorState(str, enum.Enum):
    """Monitor state enumeration."""

    NORMAL = "Normal"
    WARNING = "Warning"
    CRITICAL = "Critical"
    MISSING_DATA = "Missing Data"


# Association table for monitor-tag many-to-many relationship
monitor_tags = Table(
    "monitor_tags",
    Base.metadata,
    Column("monitor_id", Integer, ForeignKey("monitor.id")),
    Column("tag_id", Integer, ForeignKey("tags.id")),
)


class Monitor(Base):
    """
    Monitor model representing a system or service being monitored.

    Attributes:
        id: Unique identifier
        name: Monitor name
        statuses: Relationship to monitor statuses
        tags: Relationship to monitor tags
    """

    __tablename__ = "monitor"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    statuses = relationship("MonitorStatus", back_populates="monitor")
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
    monitor_id = Column(Integer, ForeignKey("monitor.id"))
    state = Column(Enum(MonitorState))
    timestamp = Column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    monitor = relationship("Monitor", back_populates="statuses")


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
