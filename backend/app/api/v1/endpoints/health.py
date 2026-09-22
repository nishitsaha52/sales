import asyncio

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.db.session import SessionLocal
from app.schemas.health import DependencyStatus, LiveResponse, ReadyResponse
from app.storage.client import storage_is_ready

router = APIRouter()


async def database_is_ready() -> tuple[bool, str | None]:
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # Readiness must report dependency failure without crashing.
        return False, type(exc).__name__


@router.get("/health/live", response_model=LiveResponse)
async def live() -> LiveResponse:
    return LiveResponse()


@router.get("/health/ready", response_model=ReadyResponse)
async def ready(response: Response) -> ReadyResponse:
    database, object_storage = await asyncio.gather(
        database_is_ready(), asyncio.to_thread(storage_is_ready)
    )
    services = {
        "postgres": DependencyStatus(status="ok" if database[0] else "error", detail=database[1]),
        "minio": DependencyStatus(
            status="ok" if object_storage[0] else "error", detail=object_storage[1]
        ),
    }
    is_ready = all(service.status == "ok" for service in services.values())
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return ReadyResponse(status="ok" if is_ready else "degraded", services=services)
