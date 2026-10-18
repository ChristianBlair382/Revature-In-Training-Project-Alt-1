import logging
from urllib.parse import urlsplit

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pymongo.errors import DuplicateKeyError
from starlette.concurrency import run_in_threadpool

from app.dependencies_mongo import require_permission
from app.orm_models.field_job_mongo import Field_Job
from app.orm_models.service_report_mongo import Service_Report
from app.orm_models.user_mongo import User
from app.schemas.service_report_mongo import (
    Service_Report_Create,
    Service_Report_Read,
    Service_Report_Update,
)
from scripts.upload_service_report import BUCKET_NAME, upload_to_s3

router = APIRouter(prefix="/service_reports", tags=["service_reports"])
logger = logging.getLogger(__name__)
DIAGNOSTICS_PREFIX = "service_reports/"

def service_report_not_found(report_id: PydanticObjectId) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Service Report '{report_id}' does not exist.",
    )

async def get_field_job(field_job_id: PydanticObjectId) -> Field_Job:
    field_job = await Field_Job.get(field_job_id)
    if field_job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Field Job '{field_job_id}' does not exist.",
        )
    return field_job

def list_diagnostic_keys() -> set[str]:
    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_objects_v2")
    keys: set[str] = set()
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix=DIAGNOSTICS_PREFIX):
        keys.update(obj["Key"] for obj in page.get("Contents", []))
    return keys

def get_report_key(file_url: str) -> str | None:
    try:
        parsed_url = urlsplit(file_url)
    except ValueError:
        return None
    if parsed_url.scheme != "s3" or parsed_url.netloc != BUCKET_NAME:
        return None
    key = parsed_url.path.lstrip("/")
    return key if key.startswith(DIAGNOSTICS_PREFIX) else None

@router.get("", response_model=list[Service_Report_Read])
async def list_service_reports(
    _: User = Depends(require_permission("service_reports:read")),
) -> list[Service_Report]:
    return await Service_Report.find_all().sort("+id").to_list()

@router.get("/verification")
async def verify_service_report_uploads(
    _: User = Depends(require_permission("service_reports:read")),
) -> list[dict[str, str | bool]]:
    reports = await Service_Report.find_all().sort("+id").to_list()
    try:
        keys = await run_in_threadpool(list_diagnostic_keys)
    except (BotoCoreError, ClientError) as exc:
        logger.exception("Could not verify service report files in S3.")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not verify service report files in storage.",
        ) from exc

    return [
        {
            "service_report_id": str(report.id),
            "verified": (key in keys if (key := get_report_key(report.file_url)) else False),
        }
        for report in reports
    ]

@router.get("/{service_report_id}", response_model=Service_Report_Read)
async def find_service_report_by_id(
    service_report_id: PydanticObjectId,
    _: User = Depends(require_permission("service_reports:read")),
) -> Service_Report:
    target_report = await Service_Report.get(service_report_id)
    if target_report is None:
        raise service_report_not_found(service_report_id)
    return target_report

@router.patch("/{service_report_id}", response_model=Service_Report_Read)
async def update_service_report(
    service_report_id: PydanticObjectId,
    payload: Service_Report_Update,
    _: User = Depends(require_permission("service_reports:update")),
) -> Service_Report:
    target_report = await Service_Report.get(service_report_id)
    if target_report is None:
        raise service_report_not_found(service_report_id)

    changes = payload.model_dump(exclude_unset=True, exclude_none=True)
    if "field_job_id" in changes:
        changes["field_job"] = await get_field_job(changes.pop("field_job_id"))

    for field, value in changes.items():
        setattr(target_report, field, value)

    try:
        await target_report.save()
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service report file URL already exists.",
        ) from exc
    return target_report

@router.post(
    "",
    response_model=Service_Report_Read,
    status_code=status.HTTP_201_CREATED,
)
async def create_new_service_report(
    payload: Service_Report_Create,
    _: User = Depends(require_permission("service_reports:create")),
) -> Service_Report:
    report_data = payload.model_dump()
    field_job = await get_field_job(report_data.pop("field_job_id"))
    new_report = Service_Report(**report_data, field_job=field_job)
    try:
        await new_report.insert()
    except DuplicateKeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service report file URL already exists.",
        ) from exc
    return new_report

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_service_report_file(
    file: UploadFile = File(...),
    _: User = Depends(require_permission("service_reports:create")),
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

@router.delete(
    "/{service_report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_report(
    service_report_id: PydanticObjectId,
    _: User = Depends(require_permission("service_reports:delete")),
) -> Response:
    target_report = await Service_Report.get(service_report_id)
    if target_report is None:
        raise service_report_not_found(service_report_id)

    await target_report.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
