from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets

from app.core.config import settings


# =====================================================
# PASSWORD HASHING
# =====================================================
# bcrypt has a 72-byte password limit.
# bcrypt__truncate_error=False prevents the app from crashing
# if a password is longer than 72 bytes.
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def normalize_password(password: str) -> str:
    """
    Clean password before hashing or verification.
    Do not use this for JWT tokens.
    """
    if password is None:
        raise ValueError("Password cannot be empty")

    return password.strip()


def hash_password(password: str) -> str:
    """
    Hash plain user password only.
    Do not pass access_token or refresh_token here.
    """
    clean_password = normalize_password(password)
    return pwd_context.hash(clean_password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify user plain password against hashed password from database.
    """
    clean_password = normalize_password(plain_password)
    return pwd_context.verify(clean_password, hashed_password)


# =====================================================
# JWT TOKEN CREATION
# =====================================================
def create_access_token(data: dict[str, Any]) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload.update(
        {
            "exp": expire,
            "type": "refresh",
        }
    )

    return jwt.encode(
        payload,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# =====================================================
# JWT TOKEN DECODING
# =====================================================
def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.REFRESH_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        return None


# =====================================================
# TOKEN RESPONSE
# =====================================================
def create_user_tokens(user) -> dict[str, str]:
    data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
    }

    return {
        "access_token": create_access_token(data),
        "refresh_token": create_refresh_token(data),
        "token_type": "bearer",
    }
    
    

 

def generate_otp() -> str:
    """Cryptographically secure 6-digit OTP."""
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return hash_password(otp)


def verify_otp_hash(otp: str, otp_hash: str) -> bool:
    return verify_password(otp, otp_hash)