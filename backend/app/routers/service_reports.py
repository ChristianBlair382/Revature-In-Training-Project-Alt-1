import logging

from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from starlette.concurrency import run_in_threadpool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, get_current_user, require_role
from app.orm_models import Service_Report, User, USER_ROLE
from app.schemas import Service_Report_Create, Service_Report_Read, Service_Report_Update
from scripts.upload_service_report import upload_to_s3
from scripts.verify_service_report import verify_service_report_files

router = APIRouter(prefix="/service_reports", tags=["service_reports"])
logger = logging.getLogger(__name__)

# GET Routers

@router.get("", response_model=list[Service_Report_Read])
async def list_service_reports(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    db_command = select(Service_Report).order_by(Service_Report.id)

    output = await db.execute(db_command)

    return list(output.scalars().all())

@router.get("/verification")
async def verify_service_report_uploads(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[dict[str, int | bool]]:
    output = await db.execute(select(Service_Report).order_by(Service_Report.id))
    reports = list(output.scalars().all())

    try:
        verification = await run_in_threadpool(
            verify_service_report_files,
            {report.id: report.file_url for report in reports},
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Could not verify service report files in S3.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not verify service report files in storage.",
        ) from exc

    return [
        {"service_report_id": report.id, "verified": verification[report.id]}
        for report in reports
    ]

@router.get("/{service_report_id}", response_model=Service_Report_Read)
async def find_service_report_by_id(
    service_report_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user)
):
    target_service_report = await db.get(Service_Report, service_report_id)

    if (not target_service_report):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service Report '{service_report_id}' does not exist."
        )
    return target_service_report

# PATCH Router

@router.patch("/{service_report_id}", response_model=Service_Report_Read)
async def update_service_report(
    service_report_id: int,
    payload: Service_Report_Update,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH))
):
    target_service_report = await db.get(Service_Report, service_report_id)
    if (not target_service_report):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service Report '{service_report_id}' does not exist."
        )

    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(target_service_report, field, value)
    
    await db.commit()
    await db.refresh(target_service_report)
    return target_service_report

# POST Router

@router.post("", response_model=Service_Report_Read, status_code=status.HTTP_201_CREATED)
async def create_new_service_report(
    payload: Service_Report_Create,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH))
):
    new_service_report = Service_Report(**payload.model_dump())
    db.add(new_service_report)
    await db.commit()
    await db.refresh(new_service_report)
    return new_service_report

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_service_report_file(
    file: UploadFile = File(...),
    _: User = Depends(require_role(USER_ROLE.FOA, USER_ROLE.FH)),
) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A file must be selected for upload.",
        )

    try:
        file_url = await run_in_threadpool(
            upload_to_s3,
            file.file,
            file.filename,
            file.content_type,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Could not upload service report file to S3.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not upload service report file to storage.",
        ) from exc

    return {"file_url": file_url}

# DELETE Router

@router.delete("/{service_report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service_report(
    service_report_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role(USER_ROLE.FOA))
):
    target_service_report = await db.get(Service_Report, service_report_id)
    if (not target_service_report):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service Report '{service_report_id}' does not exist."
        )

    await db.delete(target_service_report)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)