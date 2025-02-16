from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from app.api.dependencies import get_db
from app.models.monitor import Monitor, MonitorStatus, Tag, monitor_tags
from app.schemas.monitor import MonitorCreate, MonitorStatusUpdate, MonitorStatusResponse

router = APIRouter()

# Move all your endpoint functions here and replace @app with @router 