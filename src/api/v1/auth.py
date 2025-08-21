from fastapi import APIRouter, Depends, Form, HTTPException

from schemas.auth import RefreshRequest, Token
from schemas.user import UserCreate, UserPublic
from services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
async def login(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.authenticate_user(user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


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
        raise HTTPException(status_code=401, detail=str(e))

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
