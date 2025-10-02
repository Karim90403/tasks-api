import datetime
from pathlib import Path
from typing import List

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from starlette.requests import Request

from core.dependencies import get_current_user
from core.environment_config import settings
from core.functions import _safe_name
from schemas.request.project_change import UploadResult
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

@router.post(
    "/projects/{project_id}/files",
    response_model=List[UploadResult],
    status_code=status.HTTP_201_CREATED,
)
async def upload_project_files(
    request: Request,
    project_id: str,
    stage_id: str,
    work_type_id: str,
    task_id: str,
    subtask_id: str,
    files: List[UploadFile] = File(...),
    current_user: UserInDB = Depends(get_current_user),
    service: ForemanService = Depends(get_foreman_service),
):
    project_dir = Path(settings.project.file_dir) / _safe_name(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    results: List[UploadResult] = []
    new_links: List[dict] = []

    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for f in files:
        safe_base = _safe_name(f.filename or "file.bin")
        target_path = project_dir / f"{ts}_{safe_base}"

        size = 0
        async with aiofiles.open(target_path, "wb") as out:
            while True:
                chunk = await f.read(1024 * 1024)  # 1MB
                if not chunk:
                    break
                size += len(chunk)
                await out.write(chunk)

        base = str(request.base_url).rstrip("/")
        rel_url = f"/files/{_safe_name(project_id)}/{target_path.name}"
        abs_url = f"{base}{rel_url}"

        results.append(
            UploadResult(
                filename=target_path.name,
                size=size,
                url=rel_url,
                content_type=f.content_type or "application/octet-stream",
                stage_id=stage_id,
                task_id=task_id,
                subtask_id=subtask_id,
            )
        )

        # Объект для reportLinks: используем имя файла как title
        new_links.append({"title": safe_base, "href": abs_url})

    # <<< ВАЖНО >>> после успешной записи на диск — обновим документ проекта в Elasticsearch
    updated = await service.add_report_links(
        project_id=project_id,
        stage_id=stage_id,
        work_type_id=work_type_id,
        task_id=task_id,
        subtask_id=subtask_id,
        links=new_links,
    )

    if updated.get("result") == "not_found":
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")

    return results
