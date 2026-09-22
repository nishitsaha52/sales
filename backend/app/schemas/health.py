from typing import Literal

from pydantic import BaseModel


class LiveResponse(BaseModel):
    status: Literal["ok"] = "ok"


class DependencyStatus(BaseModel):
    status: Literal["ok", "error"]
    detail: str | None = None


class ReadyResponse(BaseModel):
    status: Literal["ok", "degraded"]
    services: dict[str, DependencyStatus]
