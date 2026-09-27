from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_irrigation_service
from app.models.irrigation import IrrigationEventCreate, IrrigationEventPublic
from app.models.user import UserInDB
from app.services.irrigation_service import IrrigationService

router = APIRouter(prefix="/irrigation", tags=["Irrigation"])


@router.post("", response_model=IrrigationEventPublic, status_code=201)
async def record_irrigation_event(
    payload: IrrigationEventCreate,
    irrigation_service: Annotated[IrrigationService, Depends(get_irrigation_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    event = await irrigation_service.record_event(payload)
    return IrrigationEventPublic(**event.model_dump())


@router.get("/trays/{tray_id}", response_model=list[IrrigationEventPublic])
async def list_irrigation_events(
    tray_id: str,
    irrigation_service: Annotated[IrrigationService, Depends(get_irrigation_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    events = await irrigation_service.list_for_tray(tray_id, skip=skip, limit=limit)
    return [IrrigationEventPublic(**e.model_dump()) for e in events]
