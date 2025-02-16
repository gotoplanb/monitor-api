from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from app.api.dependencies import get_db
from app.models.monitor import Monitor, MonitorStatus, Tag, monitor_tags, MonitorState
from app.schemas.monitor import MonitorCreate, MonitorStatusUpdate, MonitorStatusResponse

router = APIRouter(prefix="/monitors", tags=["monitors"])

@router.post("/", response_model=MonitorCreate)
def create_monitor(monitor: MonitorCreate, db: Session = Depends(get_db)):
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
def set_monitor_state(monitor_id: int, status: MonitorStatusUpdate, db: Session = Depends(get_db)):
    monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
    if not monitor:
        raise HTTPException(status_code=404, detail="Monitor not found")
    
    new_status = MonitorStatus(monitor_id=monitor.id, state=status.state)
    db.add(new_status)
    db.commit()
    return {"message": "State updated successfully"}

@router.get("/{monitor_id}/state/", response_model=MonitorStatusResponse)
def get_monitor_state(monitor_id: int, db: Session = Depends(get_db)):
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
        tags=[tag.name for tag in monitor.tags]
    )

@router.get("/statuses/", response_model=List[MonitorStatusResponse])
def get_all_monitor_states(db: Session = Depends(get_db)):
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
            tags=[tag.name for tag in db.query(Monitor).filter(Monitor.id == monitor_id).first().tags]
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
        raise HTTPException(status_code=404, detail="No monitors found with all specified tags")

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
                    tags=[tag.name for tag in monitor.tags]
                )
            )

    return latest_states 