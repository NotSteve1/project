import random
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.user_model import User, UserRole
from app.models.email_otp_model import EmailVerificationOTP
from app.schemas.user_schema import UserCreate
from app.schemas.auth_schema import LoginRequest, VerifyEmailRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email import send_otp_email


OTP_EXPIRY_MINUTES = 10


def register_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        return None

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hash_password(user_data.password),
        is_active=False,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    _generate_and_send_otp(db, new_user)

    return new_user


def _generate_and_send_otp(db: Session, user: User) -> None:
    otp = str(random.randint(100000, 999999))

    otp_row = EmailVerificationOTP(
        user_id=user.id,
        otp_hash=hash_password(otp),
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(otp_row)
    db.commit()

    asyncio.run(send_otp_email(user.email, otp)) 


def verify_email(db: Session, data: VerifyEmailRequest) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return "not_found"

    otp_row = (
        db.query(EmailVerificationOTP)
        .filter(EmailVerificationOTP.user_id == user.id, EmailVerificationOTP.is_used == False)
        .order_by(EmailVerificationOTP.created_at.desc())
        .first()
    )
    if not otp_row:
        return "not_found"

    if datetime.now(timezone.utc) > otp_row.expires_at:
        return "expired"

    otp_row.attempts += 1
    if not verify_password(data.otp, otp_row.otp_hash):
        db.commit()
        return "invalid"

    otp_row.is_used = True
    user.is_active = True
    db.commit()

    return "success"


def login_user(db: Session, data: LoginRequest) -> tuple[str, User | None]:
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return "not_found", None

    if not verify_password(data.password, user.password):
        return "wrong_password", None

    if not user.is_active:
        return "not_verified", None

    return "success", user

def resend_otp(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return "not_found"

    if user.is_active:
        return "already_verified"

    db.query(EmailVerificationOTP).filter(
        EmailVerificationOTP.user_id == user.id,
        EmailVerificationOTP.is_used == False,
    ).update({"is_used": True})
    db.commit()

    _generate_and_send_otp(db, user)
    return "sent"

def bootstrap_admin(db: Session, email: str) -> str:
    """Returns: 'success' | 'admin_exists' | 'user_not_found'"""
    existing_admin = db.query(User).filter(
        User.role.in_([UserRole.ADMIN, UserRole.SUPER_ADMIN])
    ).first()
    if existing_admin:
        return "admin_exists"

    user = db.query(User).filter(User.email == email).first()
    if not user:
        return "user_not_found"

    user.role = UserRole.SUPER_ADMIN
    db.commit()
    return "success"