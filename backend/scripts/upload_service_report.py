from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

import boto3

BUCKET_NAME = "agricore-service-reports-cb2478"

def upload_to_s3(
    file_obj: BinaryIO,
    filename: str,
    content_type: str | None = None,
) -> str:
    safe_filename = Path(filename.replace("\\", "/")).name.strip()
    if not safe_filename:
        raise ValueError("A filename is required to upload a service report.")

    s3_key = f"service_reports/{uuid4().hex}_{safe_filename}"
    extra_args = {"ContentType": content_type} if content_type else {}

    s3_client = boto3.client("s3")
    s3_client.upload_fileobj(file_obj, BUCKET_NAME, s3_key, ExtraArgs=extra_args)
    return f"s3://{BUCKET_NAME}/{s3_key}"
