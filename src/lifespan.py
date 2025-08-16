import contextlib
from typing import AsyncIterator

from fastapi import FastAPI


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Init all managers
    yield
    # Close all managers
