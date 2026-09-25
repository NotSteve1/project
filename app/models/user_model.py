import uuid
import enum
from datetime import datetime, timedelta, timezone

from sqlalchemy import String, Boolean, DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.movie_model import Movie
    from app.models.rating_model import Rating


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        index=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.USER,
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    reset_otps: Mapped[list["PasswordResetOTP"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    movies_created: Mapped[list["Movie"]] = relationship(
        back_populates="creator",
        foreign_keys="Movie.created_by",
        cascade="all, delete-orphan",
    )

    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )    

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )


class PasswordResetOTP(Base):
    __tablename__ = "password_reset_otps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # store a HASH of the OTP, never the raw code
    otp_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    attempts: Mapped[int] = mapped_column(default=0, nullable=False)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(back_populates="reset_otps")