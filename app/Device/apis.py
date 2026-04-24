from fastapi import APIRouter

from app.core.tags import RouteTags
from app.Device.routes.base import router as base_router
from app.Device.routes.relay import router as relay_router

# Globals
router = APIRouter()
tags = RouteTags()

# Routes
router.include_router(base_router, prefix="/devices")
router.include_router(relay_router, prefix="/devices/relay")
