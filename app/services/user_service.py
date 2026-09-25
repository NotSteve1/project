import uuid
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.user_model import User, UserRole, PasswordResetOTP
from app.schemas.user_schema import UserCreate, AdminCreateUser
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.utils.file_storage import (
    save_profile_image,
    delete_profile_image,
    rename_user_media_dir,
)


def create_user(db: Session, data: UserCreate):
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        return None

    user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=UserRole.USER,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def admin_create_user(db: Session, data: AdminCreateUser):
    existing_user = db.query(User).filter(User.email == data.email).first()

    if existing_user:
        return None

    user = User(
        full_name=data.full_name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    if not user.is_active:
        return None

    return user


def get_user_by_id(db: Session, user_id: uuid.UUID):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def update_user(
    db: Session,
    user_id: uuid.UUID,
    full_name: str | None = None,
    email: str | None = None,
    image: UploadFile | None = None,
):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    old_full_name = user.full_name

    if email is not None and email != user.email:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return "email_taken"
        user.email = email

    if full_name is not None:
        user.full_name = full_name

    if full_name is not None and full_name != old_full_name:
        rename_user_media_dir(user, old_full_name)

    if image is not None:
        user.profile_image = save_profile_image(user, image)

    db.commit()
    db.refresh(user)

    return user


def remove_profile_image(db: Session, user: User) -> User:
    delete_profile_image(user)
    user.profile_image = None

    db.commit()
    db.refresh(user)

    return user


def update_user_role(db: Session, user_id: uuid.UUID, role: UserRole):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user


def delete_user(db: Session, user_id: uuid.UUID):
    user = get_user_by_id(db, user_id)

    if not user:
        return None

    db.delete(user)
    db.commit()

    return user

def change_password(db: Session, user: User, current_password: str, new_password: str) -> str:
    if not verify_password(current_password, user.password):
        return "wrong_password"

    user.password = hash_password(new_password)
    db.commit()

    return "success"