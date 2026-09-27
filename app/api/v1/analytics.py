"""
Flat JSON aggregation endpoints intended as a Power BI "Web" data source.
Point Power BI's Web connector at, e.g., {base_url}/api/v1/analytics/tray-summary
and it'll parse straight into a table. For a live/refreshable connection at
scale, prefer the official MongoDB ODBC/ADO.NET connector directly against
the same database instead of polling these endpoints.
"""
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_analytics_service, require_role
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/tray-summary", dependencies=[Depends(require_role("admin", "grower"))])
async def tray_summary(analytics: Annotated[AnalyticsService, Depends(get_analytics_service)]):
    return await analytics.tray_summary()


@router.get("/water-usage", dependencies=[Depends(require_role("admin", "grower"))])
async def water_usage(analytics: Annotated[AnalyticsService, Depends(get_analytics_service)]):
    return await analytics.water_usage_by_tray()


@router.get("/prediction-accuracy", dependencies=[Depends(require_role("admin", "grower"))])
async def prediction_accuracy(analytics: Annotated[AnalyticsService, Depends(get_analytics_service)]):
    return await analytics.prediction_accuracy()
