from fastapi import APIRouter, Depends, Form, HTTPException

from core.dependencies import check_project_access
from schemas.auth import RefreshRequest, Token
from schemas.user import UserCreate, UserPublic, UserInDB
from services.auth_service import AuthService, get_auth_service
from fastapi import Response

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

@router.post("/login", response_model=Token)
async def login(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.authenticate_user(user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post("/loginform", response_model=Token)
async def login_form(
    username: str = Form(...),
    password: str = Form(...),
    service: AuthService = Depends(get_auth_service),
):
    """
    Логин через form-data (для Swagger UI, т.к. OAuth2PasswordBearer ожидает form).
    """
    try:
        return await service.authenticate_user(username, password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e

@router.post("/refresh", response_model=Token)
async def refresh(body: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    from core.security import try_decode_refresh
    payload, err = try_decode_refresh(body.refresh_token)
    if err:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return await service.refresh_tokens(sub)

@router.get(
    "/manager/users",
    status_code=200,
    dependencies=[Depends(check_project_access)]
)
async def list_users(
        service: AuthService = Depends(get_auth_service),
        current_user: UserInDB = Depends(check_project_access),
):
    if current_user.role == "root":
        return await service.list_users()


@router.post("/manager/projects/{project_id}/assign-manager/{user_id}", status_code=204, dependencies=[Depends(check_project_access)])
async def assign_manager_to_project(
    project_id: str,
    user_id: str,
    service: AuthService = Depends(get_auth_service)
):
    # проверка, что пользователь существует
    target_user = await service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    # добавим проект в список менеджера
    await service.add_project_to_user(user_id, project_id)
    return Response(status_code=204)

@router.post("/manager/projects/{project_id}/revoke-manager/{user_id}", status_code=204, dependencies=[Depends(check_project_access)])
async def revoke_manager_from_project(
    project_id: str,
    user_id: str,
    service: AuthService = Depends(get_auth_service)
):
    target_user = await service.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    await service.remove_project_from_user(user_id, project_id)
    return Response(status_code=204)

