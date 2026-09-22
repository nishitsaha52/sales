from datetime import timedelta
from functools import lru_cache
from io import BytesIO

from minio import Minio

from app.core.config import settings


@lru_cache
def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
        secure=settings.MINIO_SECURE,
    )


def ensure_private_bucket() -> None:
    client = get_minio_client()
    if not client.bucket_exists(settings.MINIO_BUCKET):
        client.make_bucket(settings.MINIO_BUCKET)


def storage_is_ready() -> tuple[bool, str | None]:
    try:
        if not get_minio_client().bucket_exists(settings.MINIO_BUCKET):
            return False, "bucket_missing"
        return True, None
    except Exception as exc:
        return False, type(exc).__name__


def put_private_object(object_key: str, data: bytes, content_type: str) -> None:
    get_minio_client().put_object(
        settings.MINIO_BUCKET,
        object_key,
        BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def presigned_download_url(object_key: str, file_name: str) -> str:
    return get_minio_client().presigned_get_object(
        settings.MINIO_BUCKET,
        object_key,
        expires=timedelta(minutes=10),
        response_headers={"response-content-disposition": f'attachment; filename="{file_name}"'},
    )
