from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, partners

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(partners.router, prefix="/partners", tags=["partners"])
