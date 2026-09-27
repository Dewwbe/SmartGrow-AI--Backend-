"""
FastAPI dependency wiring: every request gets fresh repository/service
instances bound to the shared Mongo connection, and `get_current_user`
enforces JWT auth on any endpoint that depends on it.
"""
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.config import settings
from app.core.database import get_database
from app.core.security import decode_token
from app.models.user import UserInDB
from app.repositories.irrigation_repository import IrrigationRepository
from app.repositories.prediction_repository import PredictionRepository
from app.repositories.sensor_repository import SensorRepository
from app.repositories.token_repository import TokenDenylistRepository
from app.repositories.tray_repository import TrayRepository
from app.repositories.user_repository import UserRepository
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.irrigation_service import IrrigationService
from app.services.ml_service import MLService
from app.services.sensor_service import SensorService
from app.services.tray_service import TrayService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/login", auto_error=False)

DbDep = Annotated[AsyncIOMotorDatabase, Depends(get_database)]


# --- Repositories -----------------------------------------------------------

def get_user_repository(db: DbDep) -> UserRepository:
    return UserRepository(db)


def get_tray_repository(db: DbDep) -> TrayRepository:
    return TrayRepository(db)


def get_sensor_repository(db: DbDep) -> SensorRepository:
    return SensorRepository(db)


def get_irrigation_repository(db: DbDep) -> IrrigationRepository:
    return IrrigationRepository(db)


def get_prediction_repository(db: DbDep) -> PredictionRepository:
    return PredictionRepository(db)


def get_token_denylist(db: DbDep) -> TokenDenylistRepository:
    return TokenDenylistRepository(db)


# --- Services -----------------------------------------------------------

def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    token_denylist: Annotated[TokenDenylistRepository, Depends(get_token_denylist)],
) -> AuthService:
    return AuthService(user_repo, token_denylist)


def get_tray_service(tray_repo: Annotated[TrayRepository, Depends(get_tray_repository)]) -> TrayService:
    return TrayService(tray_repo)


def get_sensor_service(
    sensor_repo: Annotated[SensorRepository, Depends(get_sensor_repository)],
    tray_repo: Annotated[TrayRepository, Depends(get_tray_repository)],
) -> SensorService:
    return SensorService(sensor_repo, tray_repo)


def get_irrigation_service(
    irrigation_repo: Annotated[IrrigationRepository, Depends(get_irrigation_repository)],
    tray_repo: Annotated[TrayRepository, Depends(get_tray_repository)],
) -> IrrigationService:
    return IrrigationService(irrigation_repo, tray_repo)


def get_ml_service(
    prediction_repo: Annotated[PredictionRepository, Depends(get_prediction_repository)],
    tray_repo: Annotated[TrayRepository, Depends(get_tray_repository)],
) -> MLService:
    return MLService(prediction_repo, tray_repo)


def get_analytics_service(db: DbDep) -> AnalyticsService:
    return AnalyticsService(db)


# --- Auth guards -----------------------------------------------------------

async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserInDB:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_error

    user = await user_repo.get_by_id(payload["sub"])
    if not user or not user.is_active:
        raise credentials_error
    return user


def require_role(*allowed_roles: str):
    async def checker(user: Annotated[UserInDB, Depends(get_current_user)]) -> UserInDB:
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return checker


async def verify_device_api_key(x_device_key: Annotated[str | None, Header()] = None) -> None:
    """Lightweight auth for ESP32 devices, which can't do a JWT login flow.
    A static per-deployment key sent as a header -- fine for a prototype;
    swap for per-device provisioned keys before any real-world pilot."""
    if x_device_key != settings.device_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device key")
