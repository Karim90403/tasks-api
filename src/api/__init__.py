from fastapi import APIRouter

from .index import router as index_router
from .v1 import v1_router

api_router = APIRouter(prefix="/api")
api_router.include_router(v1_router)

router = APIRouter()
router.include_router(index_router)
router.include_router(api_router)
