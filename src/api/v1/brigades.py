# api/brigade_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body

from core.dependencies import get_current_user
from schemas.request.brigade import BrigadeCreate
from schemas.response.brigade import BrigadeInDB
from schemas.user import UserInDB
from services.brigade_service import get_brigade_service, BrigadeService

router = APIRouter(prefix="/brigades", tags=["brigades"])


@router.post("/", response_model=BrigadeInDB, status_code=status.HTTP_201_CREATED)
async def create_brigade(
    payload: BrigadeCreate,
    service: BrigadeService = Depends(get_brigade_service),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Создать бригаду. Возвращает полный объект бригады.
    Поле members — список user_id / email.
    """
    # создаём детерминированный id и создаём бригаду
    brigade_id, _ = await service.create_or_get_brigade_by_members(
        members=payload.members, brigade_name=payload.brigade_name, created_by=payload.created_by
    )

    created = await service.get_brigade(brigade_id)
    if not created:
        # неожиданный кейс — поднять ошибку
        raise HTTPException(status_code=500, detail="Brigade created but not retrievable")
    return created


@router.get("/{brigade_id}", response_model=BrigadeInDB)
async def get_brigade(
    brigade_id: str,
    service: BrigadeService = Depends(get_brigade_service),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Получить бригаду по id.
    """
    doc = await service.get_brigade(brigade_id)
    if not doc:
        raise HTTPException(status_code=404, detail="brigade_not_found")
    return doc


@router.post("/lookup", response_model=BrigadeInDB)
async def lookup_or_create_brigade(
    members: List[str] = Body(..., embed=True, description="Список участников (user_id или email)"),
    brigade_name: Optional[str] = Body(None, description="Опциональное имя бригады"),
    created_by: Optional[str] = Body(None, description="Кто создаёт"),
    service: BrigadeService = Depends(get_brigade_service),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    По списку участников возвращает существующую бригаду или создаёт новую.
    Полезно при миграции или если frontend продолжает отправлять assignees.
    """
    brigade_id, doc = await service.create_or_get_brigade_by_members(
        members=members, brigade_name=brigade_name, created_by=created_by
    )
    # doc может быть None если ES вернул пусто — достанем заново
    if not doc:
        doc = await service.get_brigade(brigade_id)
    if not doc:
        raise HTTPException(status_code=500, detail="cannot_create_or_get_brigade")
    return doc


@router.get("/", response_model=List[BrigadeInDB])
async def search_brigades(
    name: Optional[str] = Query(None, description="Поиск по имени (match)"),
    member: Optional[str] = Query(None, description="Поиск по user_id участника"),
    size: int = Query(20, gt=0, le=100, description="Размер результата"),
    service: BrigadeService = Depends(get_brigade_service),
    current_user: UserInDB = Depends(get_current_user),
):
    """
    Поиск бригад. Поддерживает простой поиск по имени и/или по участнику.
    Если оба параметра не заданы — вернёт первые N (match_all).
    """

    results = await service.search_brigades(name, member, size=size)

    return results
