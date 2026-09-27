from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, get_ml_service
from app.models.prediction import PredictionInDB, PredictionRequest
from app.models.user import UserInDB
from app.services.ml_service import MLService

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionInDB, status_code=201)
async def create_prediction(
    payload: PredictionRequest,
    ml_service: Annotated[MLService, Depends(get_ml_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
):
    """Run the irrigation/moisture model for a tray's current readings and log the result."""
    return await ml_service.predict(payload)


@router.get("/trays/{tray_id}", response_model=list[PredictionInDB])
async def list_predictions(
    tray_id: str,
    ml_service: Annotated[MLService, Depends(get_ml_service)],
    current_user: Annotated[UserInDB, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
):
    return await ml_service.list_for_tray(tray_id, skip=skip, limit=limit)
