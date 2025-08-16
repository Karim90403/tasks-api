from fastapi import APIRouter, status

router = APIRouter(tags=["test route"])


@router.get(
    "/healthcheck",
    status_code=status.HTTP_200_OK,
)
async def healthcheck():
    return
