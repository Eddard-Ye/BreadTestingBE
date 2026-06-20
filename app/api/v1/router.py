from fastapi import APIRouter

from app.api.v1.endpoints import auth, health, measurements, recipes, sensors

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(health.router, tags=["health"])
