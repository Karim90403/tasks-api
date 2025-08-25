from typing import List

from fastapi import APIRouter, Depends, status

from core.dependencies import get_current_user
from schemas.user import UserInDB
from services.foreman_service import ForemanService, get_foreman_service

router = APIRouter(prefix="/api/foreman", tags=["foreman"])


@router.get("/projects", status_code=status.HTTP_200_OK)
async def get_projects(
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.list_projects(current_user.id)


@router.get("/tasks", status_code=status.HTTP_200_OK)
async def get_tasks(
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.list_tasks(current_user.id)

@router.post("/shift/start", status_code=status.HTTP_200_OK)
async def start_shift(
    task_ids: List[str],
    subtask_ids: List[str],
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    await service.start_shift(current_user.id, task_ids, subtask_ids)
    return {"result": "shift started"}


@router.post("/shift/stop", status_code=status.HTTP_200_OK)
async def stop_shift(
    task_ids: List[str],
    subtask_ids: List[str],
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    await service.stop_shift(current_user.id, task_ids, subtask_ids)
    return {"result": "shift stopped"}


@router.get("/shift/history", status_code=status.HTTP_200_OK)
async def shift_history(
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.shift_history(current_user.id)


@router.get("/shift/status", status_code=status.HTTP_200_OK)
async def shift_status(
    service: ForemanService = Depends(get_foreman_service),
    current_user: UserInDB = Depends(get_current_user),
):
    return await service.shift_status(current_user.id)
