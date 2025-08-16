from fastapi import APIRouter

from .index import router as index_router
from .v1 import v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
router.include_router(index_router)

