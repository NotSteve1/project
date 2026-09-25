import re
import uuid
from pathlib import Path

from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.models.user_model import User


def slugify(value: str) -> str:
    """Turn a full name into a filesystem-safe slug."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "user"


def get_user_folder_name(user: User) -> str:
    """
    Folder is based on the user's full name, with a short id suffix
    to guarantee uniqueness (two users can share a full name, but not a UUID).
    """
    return f"{slugify(user.full_name)}-{str(user.id)[:8]}"


def get_user_media_dir(user: User) -> Path:
    folder = settings.MEDIA_ROOT / "users" / get_user_folder_name(user)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def rename_user_media_dir(user: User, old_full_name: str) -> None:
    """
    Call this BEFORE committing a full_name change, if the user already
    has a media folder, so the folder tracks their new name.
    """
    old_folder = settings.MEDIA_ROOT / "users" / f"{slugify(old_full_name)}-{str(user.id)[:8]}"
    new_folder = settings.MEDIA_ROOT / "users" / get_user_folder_name(user)

    if old_folder.exists() and old_folder != new_folder:
        old_folder.rename(new_folder)

        # profile_image path stored on the user references the old folder - fix it up
        if user.profile_image:
            filename = Path(user.profile_image).name
            user.profile_image = f"{settings.MEDIA_URL}/users/{get_user_folder_name(user)}/{filename}"


def _validate_image(file: UploadFile, contents: bytes) -> str:
    if file.content_type not in settings.ALLOWED_IMAGE_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {file.content_type}",
        )

    if len(contents) > settings.MAX_PROFILE_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image exceeds the 5MB size limit",
        )

    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    return ext_map[file.content_type]


def delete_profile_image(user: User) -> None:
    """Remove any existing profile image file(s) for this user (any extension)."""
    folder = get_user_media_dir(user)
    for existing in folder.glob("profile.*"):
        existing.unlink(missing_ok=True)


def save_profile_image(user: User, file: UploadFile) -> str:
    """
    Saves the uploaded file into the user's media folder as 'profile.<ext>',
    replacing any previous profile image. Returns the public URL path
    to store on user.profile_image.
    """
    contents = file.file.read()
    ext = _validate_image(file, contents)

    folder = get_user_media_dir(user)

    # remove old profile image regardless of its previous extension
    delete_profile_image(user)

    dest = folder / f"profile{ext}"
    with open(dest, "wb") as f:
        f.write(contents)

    return f"{settings.MEDIA_URL}/users/{get_user_folder_name(user)}/profile{ext}"