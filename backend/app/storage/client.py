from functools import lru_cache

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
