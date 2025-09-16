# app/routes/health_ready.py
from fastapi import APIRouter, HTTPException
from app.core.logger import get_logger
from app.core.db import check_db
from app.core.redis_client import ping_redis
from app.core.metrics import metrics_response

log = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/ping")
async def ping():
    return {"status": "ok"}

@router.get("/ready")
async def ready():
    db_ok = await check_db()
    redis_ok = await ping_redis()
    if db_ok and redis_ok:
        return {"ready": True}
    raise HTTPException(status_code=503, detail={"ready": False, "db": db_ok, "redis": redis_ok})

# Prometheus scrape endpoint
@router.get("/metrics")
async def metrics():
    return metrics_response()
