from app.config import settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .routers import auth, equipments, farms, field_jobs, hands, service_reports, supervisors, users

FRONTEND_ORIGIN = settings.frontend_origin

app = FastAPI(
    title="AgriCore",
    description="Fleet Management API for Prairie Crest Agricultural Cooperative farmlands and equipment",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "OK"}

@app.get("/version", tags=["version"])
async def version_check() -> dict[str, str]:
    return {"version": app.version}

app.include_router(farms.router)
app.include_router(equipments.router)
app.include_router(field_jobs.router)
app.include_router(service_reports.router)
app.include_router(hands.router)
app.include_router(supervisors.router)
app.include_router(auth.router)
app.include_router(users.router)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": "Database constraint violation."}
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": "Unknown error detected. Please see the developer console for more details."}
    )