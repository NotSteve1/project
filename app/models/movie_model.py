import uuid
import enum
from datetime import datetime
from sqlalchemy import BigInteger, Enum, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user_model import User
    from app.models.rating_model import Rating

class MovieStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NOT_APPROVED = "not_approved"

class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    genre: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    release_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    status: Mapped[MovieStatus] = mapped_column(
        Enum(MovieStatus),
        default=MovieStatus.PENDING,
        nullable=False
    )

    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,  
        index=True,
    )
    
    approved_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    video_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    video_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    creator: Mapped["User"] = relationship(back_populates="movies_created", foreign_keys=[created_by])

    ratings: Mapped[list["Rating"]] = relationship(
        back_populates="movie",
        cascade="all, delete-orphan",
    )

    # NOTE: average rating is intentionally NOT stored as a column.
    # Compute it on read, e.g. in the service layer:
    #
    #   from sqlalchemy import func, select
    #   stmt = (
    #       select(func.avg(Rating.rating))
    #       .where(Rating.movie_id == movie.id)
    #   )
    #   avg_rating = (await db.execute(stmt)).scalar()  # None if no ratings
