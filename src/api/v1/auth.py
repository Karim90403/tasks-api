from fastapi import APIRouter, Depends, HTTPException

from schemas.auth import Token
from schemas.user import UserPublic, UserCreate
from services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserPublic)
def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    try:
        return service.authenticate_user(user.email, user.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
