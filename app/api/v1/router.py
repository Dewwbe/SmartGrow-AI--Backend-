from fastapi import APIRouter

from app.api.v1 import agent, analytics, auth, irrigation, predictions, sensors, trays, users

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(trays.router)
api_router.include_router(sensors.router)
api_router.include_router(irrigation.router)
api_router.include_router(predictions.router)
api_router.include_router(analytics.router)
api_router.include_router(agent.router)
