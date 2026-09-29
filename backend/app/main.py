from app.config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, equipments, farms, field_jobs, hands, service_reports, supervisors

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

app.include_router(farms.router)
app.include_router(equipments.router)
app.include_router(field_jobs.router)
app.include_router(service_reports.router)
app.include_router(hands.router)
app.include_router(supervisors.router)
app.include_router(auth.router)

@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status", "OK"}

@app.get("/version", tags=["version"])
async def version_check() -> dict[str, str]:
    return {"version", app.version}