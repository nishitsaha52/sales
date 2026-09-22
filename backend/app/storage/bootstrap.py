from app.core.config import settings
from app.storage.client import ensure_private_bucket


def main() -> None:
    ensure_private_bucket()
    print(f"MinIO bucket '{settings.MINIO_BUCKET}' is ready and private.")


if __name__ == "__main__":
    main()
