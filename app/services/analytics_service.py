"""
Aggregation endpoints built specifically to be easy for Power BI (or any
BI tool) to consume as a flat "Web" JSON data source: one row per tray-day,
no nested objects, stable field names.
"""
from motor.motor_asyncio import AsyncIOMotorDatabase


class AnalyticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def tray_summary(self) -> list[dict]:
        pipeline = [
            {
                "$group": {
                    "_id": "$tray_id",
                    "reading_count": {"$sum": 1},
                    "avg_moisture_pct": {"$avg": "$substrate_moisture_pct"},
                    "avg_temperature_c": {"$avg": "$temperature_c"},
                    "avg_humidity_pct": {"$avg": "$relative_humidity_pct"},
                    "avg_light_lux": {"$avg": "$light_lux"},
                }
            },
            {"$project": {"_id": 0, "tray_id": {"$toString": "$_id"},
                           "reading_count": 1, "avg_moisture_pct": 1,
                           "avg_temperature_c": 1, "avg_humidity_pct": 1, "avg_light_lux": 1}},
        ]
        return [doc async for doc in self.db["sensor_readings"].aggregate(pipeline)]

    async def water_usage_by_tray(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$tray_id", "total_volume_ml": {"$sum": "$volume_ml"}, "events": {"$sum": 1}}},
            {"$project": {"_id": 0, "tray_id": {"$toString": "$_id"}, "total_volume_ml": 1, "events": 1}},
        ]
        return [doc async for doc in self.db["irrigation_events"].aggregate(pipeline)]

    async def prediction_accuracy(self) -> list[dict]:
        """Predicted vs actual moisture, for the model-evaluation metrics (MAE/RMSE) called for in the proposal."""
        pipeline = [
            {"$match": {"actual_moisture_pct_after": {"$exists": True}, "predicted_moisture_pct": {"$exists": True}}},
            {"$project": {
                "_id": 0,
                "tray_id": {"$toString": "$tray_id"},
                "predicted_moisture_pct": 1,
                "actual_moisture_pct_after": 1,
                "abs_error": {"$abs": {"$subtract": ["$predicted_moisture_pct", "$actual_moisture_pct_after"]}},
            }},
        ]
        return [doc async for doc in self.db["irrigation_events"].aggregate(pipeline)]
