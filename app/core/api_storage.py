import uuid
import boto3
from fastapi import UploadFile, HTTPException

from app.core.config import settings

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}

s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.B2_ENDPOINT}",
    aws_access_key_id=settings.B2_KEY_ID,
    aws_secret_access_key=settings.B2_APPLICATION_KEY,
)


def upload_movie_video(file: UploadFile) -> tuple[str, int]:
    """Returns: (storage_key, size_in_bytes)"""

    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported video format. Use mp4, mov, or webm.")

    file.file.seek(0, 2)
    size_bytes = file.file.tell()
    file.file.seek(0)
    size_mb = size_bytes / (1024 * 1024)

    if size_mb > settings.MAX_VIDEO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"Video too large ({size_mb:.1f}MB). Max allowed is {settings.MAX_VIDEO_SIZE_MB}MB.",
        )

    extension = file.filename.split(".")[-1]
    key = f"movies/{uuid.uuid4()}.{extension}"

    s3_client.upload_fileobj(file.file, settings.B2_BUCKET_NAME, key)

    return key, size_bytes


def get_video_download_url(storage_key: str) -> str:
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.B2_BUCKET_NAME, "Key": storage_key},
        ExpiresIn=3600,
    )


def delete_movie_video(storage_key: str) -> None:
    try:
        s3_client.delete_object(Bucket=settings.B2_BUCKET_NAME, Key=storage_key)
    except Exception as error:
        print(f"Failed to delete B2 object {storage_key}: {error}")