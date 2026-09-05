"""Application-scoped MongoDB client used by the report persistence flow."""

from app.core.config import settings
from app.core.logging import logger

_client = None


def connect_mongodb() -> None:
    """Create and verify the single Mongo client when Mongo report mode is enabled."""
    global _client
    if settings.REPORT_STORAGE.lower() != "mongodb":
        return
    if not settings.MONGODB_URI:
        raise RuntimeError("REPORT_STORAGE=mongodb requires MONGODB_URI in api/.env")
    try:
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError("MongoDB report mode requires pymongo. Run: pip install -r requirements.txt") from exc
    _client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    _client.admin.command("ping")
    db = _client[settings.MONGODB_DATABASE]
    db.reports.create_index("report_id", unique=True)
    db.reports.create_index([("created_at", -1)])
    db.reports.create_index([("risk.urgency_score", -1)])
    db.reports.create_index("metadata.facility_id")
    db.reports.create_index("analysis.sif_potential")
    logger.info("MongoDB connected: database=%s, collection=reports", settings.MONGODB_DATABASE)


def get_mongo_db():
    if _client is None:
        raise RuntimeError("MongoDB report storage is not connected. Check MONGODB_URI and startup logs.")
    return _client[settings.MONGODB_DATABASE]


def close_mongodb() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
