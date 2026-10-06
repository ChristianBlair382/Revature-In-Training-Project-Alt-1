# Run with: python -m scripts.verify_service_report
# From: backend/ with venv active

import asyncio
from urllib.parse import urlsplit

import boto3
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.orm_models import Service_Report

BUCKET_NAME = "agricore-service-reports-cb2478"
DIAGNOSTICS_PREFIX = "service_reports/"

def extract_s3_key(file_url: str) -> str | None:
    try:
        parsed_url = urlsplit(file_url)
    except ValueError:
        return None
    if parsed_url.scheme != "s3" or parsed_url.netloc != BUCKET_NAME:
        return None

    key = parsed_url.path.lstrip("/")
    if not key.startswith(DIAGNOSTICS_PREFIX):
        return None
    return key

def list_s3_keys(bucket_name: str, prefix: str) -> set[str]:
    s3_client = boto3.client("s3")
    paginator = s3_client.get_paginator("list_objects_v2")

    keys: set[str] = set()
    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            keys.add(obj["Key"])
    return keys

def verify_service_report_files(
    file_urls: dict[int, str],
    s3_keys: set[str] | None = None,
) -> dict[int, bool]:
    if not file_urls:
        return {}
    if s3_keys is None:
        s3_keys = list_s3_keys(BUCKET_NAME, DIAGNOSTICS_PREFIX)
    return {
        report_id: (key in s3_keys if (key := extract_s3_key(file_url)) is not None else False)
        for report_id, file_url in file_urls.items()
    }

async def fetch_diagnostic_reports() -> list[Service_Report]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Service_Report).order_by(Service_Report.id))
        return list(result.scalars().all())

async def main() -> None:
    reports = await fetch_diagnostic_reports()
    s3_keys = list_s3_keys(BUCKET_NAME, DIAGNOSTICS_PREFIX)
    verification = verify_service_report_files({
        report.id: report.file_url
        for report in reports
    }, s3_keys)
    referenced_keys = {
        key
        for report in reports
        if (key := extract_s3_key(report.file_url)) is not None
    }
    healthy = [report for report in reports if verification[report.id]]
    broken = [report for report in reports if not verification[report.id]]
    orphaned_keys = s3_keys - referenced_keys

    print("\n== Healthy (database row + matching s3 file) ==")
    if not healthy:
        print(" None found. ")
    else:
        for report in healthy:
            print(f"ServiceReport {report.id}: {report.file_url}")

    print("== Broken (database row, no matching s3 file) ==")
    if not broken:
        print(" None found. ")
    else:
        for report in broken:
            print(f"ServiceReport {report.id}: {report.file_url}")

    print("== Orphaned ( s3 file with no matching database row ) ==")
    if not orphaned_keys:
        print(" None found. ")
    else:
        for key in orphaned_keys:
            print(f"s3://{BUCKET_NAME}/{key}")


if __name__ == "__main__":
    asyncio.run(main())
