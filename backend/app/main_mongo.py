from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.config import settings
from app.database_mongo import (
    close_mongo_connection,
    connect_to_mongo,
    ping_mongo,
)
from app.routers import mongo_users


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        await connect_to_mongo()
        yield
    finally:
        await close_mongo_connection()


app = FastAPI(
    title="AgriCore",
    description="MongoDB-backed AgriCore API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "OK"}


@app.get("/health/ready", tags=["health"])
async def health_readiness_check() -> JSONResponse:
    try:
        await ping_mongo()
    except (PyMongoError, RuntimeError):
        return JSONResponse(
            status_code=503,
            content={"status": "Database is currently unreachable."},
        )

    return JSONResponse(
        status_code=200,
        content={"status": "Database is currently reachable."},
    )


@app.get("/version", tags=["version"])
async def version_check() -> dict[str, str]:
    return {"version": app.version}


app.include_router(mongo_users.router)
