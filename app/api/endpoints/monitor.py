"""
Monitor API endpoints module.

This module provides FastAPI route handlers for the monitoring system.
"""

from io import BytesIO
from typing import List

import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from PIL import Image, ImageDraw
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import get_db
from app.models.monitor import Monitor, MonitorStatus, Tag, monitor_tags, MonitorState
from app.schemas.monitor import (
    MonitorCreate,
    MonitorStatusUpdate,
    MonitorStatusResponse,
)

router = APIRouter(prefix="/monitor", tags=["monitor"])

logger = logging.getLogger(__name__)


@router.post("/", response_model=MonitorCreate)
def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
    """
    Create a new monitor with optional tags.

    Args:
        monitor: Monitor creation data
        db: Database session

    Returns:
        MonitorCreate: Created monitor data

    Raises:
        HTTPException: If monitor already exists
    """
    existing_monitor = db.query(Monitor).filter(Monitor.name == monitor.name).first()
    if existing_monitor:
        raise HTTPException(status_code=400, detail="Monitor already exists")

    new_monitor = Monitor(name=monitor.name)

    # Add tags
    for tag_name in monitor.tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
        new_monitor.tags.append(tag)

    db.add(new_monitor)
    db.commit()
    db.refresh(new_monitor)

    # Create initial status
    initial_status = MonitorStatus(monitor_id=new_monitor.id, state=MonitorState.NORMAL)
    db.add(initial_status)
    db.commit()

    # Return the created monitor with its ID
    return MonitorCreate(
        id=new_monitor.id,
        name=new_monitor.name,
        tags=[tag.name for tag in new_monitor.tags],
    )


@router.post("/{monitor_id}/state/")
def set_monitor_state(
    monitor_id: int, status: MonitorStatusUpdate, db: Session = Depends(get_db)
):
    """
    Set the state of a specific monitor.

    Args:
        monitor_id: ID of the monitor to update
        status: New status data
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If monitor not found
    """
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    new_status = MonitorStatus(
        monitor_id=monitor.id, state=status.state, message=status.message
    )
    db.add(new_status)
    db.commit()
    return {"message": "State updated successfully"}


@router.get("/{monitor_id}/state/", response_model=MonitorStatusResponse)
def get_monitor_state(monitor_id: int, db: Session = Depends(get_db)):
    """
    Get the current state of a specific monitor.

    Args:
        monitor_id: ID of the monitor to query
        db: Database session

    Returns:
        MonitorStatusResponse: Monitor status data

    Raises:
        HTTPException: If monitor or state not found
    """
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    latest_status = (
        db.query(MonitorStatus)
        .filter(MonitorStatus.monitor_id == monitor_id)
        .order_by(desc(MonitorStatus.timestamp))
        .first()
    )

    if not latest_status:
        raise HTTPException(status_code=404, detail="No state found for this monitor")

    return MonitorStatusResponse(
        id=monitor_id,
        name=monitor.name,
        state=latest_status.state,
        message=latest_status.message,
        timestamp=latest_status.timestamp,
        tags=[tag.name for tag in monitor.tags],
    )


@router.get("/statuses/", response_model=List[MonitorStatusResponse])
def get_all_monitor_states(db: Session = Depends(get_db)):
    """
    Get the current state of all monitors.

    Args:
        db: Database session

    Returns:
        List[MonitorStatusResponse]: List of monitor status data
    """
    try:
        # Subquery to get the latest status for each monitor
        latest_status = (
            db.query(
                MonitorStatus.monitor_id,
                func.max(MonitorStatus.timestamp).label("max_timestamp"),
            )
            .group_by(MonitorStatus.monitor_id)
            .subquery()
        )

        # Main query joining with the subquery
        latest_states = (
            db.query(
                Monitor.id,
                Monitor.name,
                MonitorStatus.state,
                MonitorStatus.message,
                MonitorStatus.timestamp,
            )
            .join(MonitorStatus)
            .join(
                latest_status,
                and_(
                    Monitor.id == latest_status.c.monitor_id,
                    MonitorStatus.timestamp == latest_status.c.max_timestamp,
                ),
            )
            .order_by(desc(MonitorStatus.timestamp))
            .all()
        )

        if not latest_states:
            return []

        result = []
        for monitor_id, name, state, message, timestamp in latest_states:
            monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
            tags = [tag.name for tag in monitor.tags] if monitor else []

            result.append(
                MonitorStatusResponse(
                    id=monitor_id,
                    name=name,
                    state=state,
                    message=message,
                    timestamp=timestamp,
                    tags=tags,
                )
            )

        return result

    except SQLAlchemyError as e:
        logger.error("Error retrieving monitor states: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}"
        ) from e


@router.get("/statuses/by-tags/", response_model=List[MonitorStatusResponse])
def get_monitors_by_tags(tags: List[str] = Query(None), db: Session = Depends(get_db)):
    """
    Get monitors filtered by tags.

    Args:
        tags: List of tags to filter by (monitors must have all specified tags)
        db: Database session

    Returns:
        List[MonitorStatusResponse]: List of monitor statuses
    """
    if not tags:
        return []

    # Subquery to find monitors that have all specified tags
    tag_count = len(tags)
    monitors_with_all_tags = (
        db.query(Monitor.id)
        .join(monitor_tags)
        .join(Tag)
        .filter(Tag.name.in_(tags))
        .group_by(Monitor.id)
        .having(func.count(Tag.id) == tag_count)  # pylint: disable=not-callable
    )

    # Subquery to get the latest status for each monitor
    latest_status = (
        db.query(
            MonitorStatus.monitor_id,
            func.max(MonitorStatus.timestamp).label("max_timestamp"),
        )
        .group_by(MonitorStatus.monitor_id)
        .subquery()
    )

    # Main query to get monitor details with latest status
    query = (
        db.query(
            Monitor.id,
            Monitor.name,
            MonitorStatus.state,
            MonitorStatus.message,
            MonitorStatus.timestamp,
        )
        .join(MonitorStatus)
        .join(
            latest_status,
            and_(
                Monitor.id == latest_status.c.monitor_id,
                MonitorStatus.timestamp == latest_status.c.max_timestamp,
            ),
        )
        .filter(Monitor.id.in_(monitors_with_all_tags))
        .order_by(desc(MonitorStatus.timestamp))
    )

    monitors = query.all()
    result = []

    for monitor_id, name, state, message, timestamp in monitors:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        tags = [tag.name for tag in monitor.tags] if monitor else []

        result.append(
            MonitorStatusResponse(
                id=monitor_id,
                name=name,
                state=state,
                message=message,
                timestamp=timestamp,
                tags=tags,
            )
        )

    return result


@router.get("/{monitor_id}/state/badge.png")
def get_monitor_state_badge(monitor_id: int, db: Session = Depends(get_db)):
    """Get a monitor's state as a PNG badge."""
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    latest_status = (
        db.query(MonitorStatus)
        .filter(MonitorStatus.monitor_id == monitor_id)
        .order_by(desc(MonitorStatus.timestamp))
        .first()
    )

    if not latest_status:
        raise HTTPException(status_code=404, detail="No state found for this monitor")

    # Define colors for different states
    state_colors = {
        MonitorState.NORMAL: "#4CAF50",  # Green
        MonitorState.WARNING: "#FFC107",  # Yellow
        MonitorState.CRITICAL: "#F44336",  # Red
        MonitorState.MISSING_DATA: "#9E9E9E",  # Gray
    }

    # Create image
    badge_height = 20
    name_width = 100
    state_width = 80
    total_width = name_width + state_width

    img = Image.new("RGB", (total_width, badge_height), color="#555555")
    draw = ImageDraw.Draw(img)

    # Draw state background
    state_color = state_colors.get(latest_status.state, "#9E9E9E")
    draw.rectangle([(name_width, 0), (total_width, badge_height)], fill=state_color)

    # Draw text
    draw.text((5, 4), monitor.name[:12], fill="white")
    draw.text((name_width + 5, 4), latest_status.state.value, fill="white")

    # Convert image to bytes
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return Response(content=img_byte_arr.getvalue(), media_type="image/png")


@router.get("/{monitor_id}/history/", response_model=List[MonitorStatusResponse])
def get_monitor_history(
    monitor_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get paginated history of monitor states.

    Args:
        monitor_id: ID of the monitor
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session

    Returns:
        List[MonitorStatusResponse]: List of historical status records
    """
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    statuses = (
        db.query(MonitorStatus)
        .filter(MonitorStatus.monitor_id == monitor_id)
        .order_by(desc(MonitorStatus.timestamp))
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        MonitorStatusResponse(
            id=monitor_id,
            name=monitor.name,
            state=status.state,
            message=status.message,
            timestamp=status.timestamp,
            tags=[tag.name for tag in monitor.tags],
        )
        for status in statuses
    ]


@router.delete("/{monitor_id}/")
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    """
    Delete a monitor and all its associated data.

    Args:
        monitor_id: ID of the monitor to delete
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If monitor not found
    """
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")

    # Delete associated statuses first
    db.query(MonitorStatus).filter(MonitorStatus.monitor_id == monitor_id).delete()

    # Delete the monitor (this will also handle the monitor_tags associations)
    db.delete(monitor)
    db.commit()

    return {"message": "Monitor deleted successfully"}
