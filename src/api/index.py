from fastapi import FastAPI

from api.v1 import manager, foreman

app = FastAPI(title="Construction API")

app.include_router(manager.router)
app.include_router(foreman.router)


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
