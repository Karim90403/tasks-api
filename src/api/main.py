from fastapi import APIRouter, Depends, FastAPI

from api import router as top_router
from core.logguru_config import logging_dependency


def setup_routers(app: FastAPI):
    root_router = APIRouter()
    root_router.include_router(top_router)
    app.include_router(root_router, dependencies=[Depends(logging_dependency)])
