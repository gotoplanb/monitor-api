"""
Monitor API endpoints module.

This module provides FastAPI route handlers for the monitoring system.
"""

from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from PIL import Image, ImageDraw
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.monitor import Monitor, MonitorStatus, Tag, monitor_tags, MonitorState
from app.schemas.monitor import MonitorCreate, MonitorStatusUpdate, MonitorStatusResponse

router = APIRouter(prefix="/monitors", tags=["monitors"])


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
    return monitor


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

    new_status = MonitorStatus(monitor_id=monitor.id, state=status.state)
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
        name=monitor.name,
        state=latest_status.state,
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
    latest_states = (
        db.query(Monitor.id, Monitor.name, MonitorStatus.state, MonitorStatus.timestamp)
        .join(MonitorStatus)
        .group_by(Monitor.id)
        .order_by(desc(MonitorStatus.timestamp))
        .all()
    )

    if not latest_states:
        return []

    return [
        MonitorStatusResponse(
            name=name,
            state=state,
            timestamp=timestamp,
            tags=[
                tag.name
                for tag in db.query(Monitor)
                .filter(Monitor.id == monitor_id)
                .first()
                .tags
            ],
        )
        for monitor_id, name, state, timestamp in latest_states
    ]


@router.get("/statuses/by-tags/", response_model=List[MonitorStatusResponse])
def get_monitors_by_tags(tags: List[str] = Query(...), db: Session = Depends(get_db)):
    """Retrieve the latest state for all monitors that have all specified tags."""
    if not tags:
        raise HTTPException(status_code=400, detail="At least one tag must be provided")

    # Find monitors that contain all the requested tags
    subquery = (
        db.query(Monitor.id)
        .join(monitor_tags)
        .filter(monitor_tags.c.tag.in_(tags))
        .group_by(Monitor.id)
        .having(func.count(monitor_tags.c.tag) == len(tags))
        .subquery()
    )

    monitors = db.query(Monitor).filter(Monitor.id.in_(subquery)).all()

    if not monitors:
        raise HTTPException(
            status_code=404, detail="No monitors found with all specified tags"
        )

    latest_states = []
    for monitor in monitors:
        latest_status = (
            db.query(MonitorStatus)
            .filter(MonitorStatus.monitor_id == monitor.id)
            .order_by(desc(MonitorStatus.timestamp))
            .first()
        )
        if latest_status:
            latest_states.append(
                MonitorStatusResponse(
                    name=monitor.name,
                    state=latest_status.state,
                    timestamp=latest_status.timestamp,
                    tags=[tag.name for tag in monitor.tags],
                )
            )

    return latest_states


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
    db: Session = Depends(get_db)
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
            name=monitor.name,
            state=status.state,
            timestamp=status.timestamp,
            tags=[tag.name for tag in monitor.tags],
        )
        for status in statuses
    ]
