from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_tray_service
from app.models.tray import TrayCreate, TrayPublic, TrayUpdate
from app.models.user import UserInDB
from app.services.tray_service import TrayService

router = APIRouter(prefix="/trays", tags=["Trays"])


@router.post("", response_model=TrayPublic, status_code=201)
async def create_tray(
    payload: TrayCreate,
    tray_service: Annotated[TrayService, Depends(get_tray_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    tray = await tray_service.create_tray(payload, owner_id=current_user.id)
    return TrayPublic(**tray.model_dump())


@router.get("", response_model=list[TrayPublic])
async def list_trays(
    tray_service: Annotated[TrayService, Depends(get_tray_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    trays = await tray_service.list_trays(current_user.id, skip=skip, limit=limit)
    return [TrayPublic(**t.model_dump()) for t in trays]


@router.get("/{tray_id}", response_model=TrayPublic)
async def get_tray(
    tray_id: str,
    tray_service: Annotated[TrayService, Depends(get_tray_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    tray = await tray_service.get_tray(tray_id)
    return TrayPublic(**tray.model_dump())


@router.patch("/{tray_id}", response_model=TrayPublic)
async def update_tray(
    tray_id: str,
    payload: TrayUpdate,
    tray_service: Annotated[TrayService, Depends(get_tray_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    tray = await tray_service.update_tray(tray_id, payload)
    return TrayPublic(**tray.model_dump())


@router.delete("/{tray_id}", status_code=204)
async def delete_tray(
    tray_id: str,
    tray_service: Annotated[TrayService, Depends(get_tray_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    await tray_service.delete_tray(tray_id)
