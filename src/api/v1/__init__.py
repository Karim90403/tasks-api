from fastapi import APIRouter

from api.v1 import auth, foreman, manager

v1_router = APIRouter(prefix="/v1")

v1_router.include_router(manager.router)
v1_router.include_router(foreman.router)
v1_router.include_router(auth.router)


