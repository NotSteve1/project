import uuid

from ark_py import Ark, ArkError
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.movie_model import Movie, MovieStatus
from app.models.rating_model import Rating
from app.schemas.movie_schema import MovieCreate

from app.core.config import settings
from app.core.api_storage import delete_movie_video


def get_movie_by_id(db: Session, movie_id: uuid.UUID) -> Movie | None:
    return db.query(Movie).filter(Movie.id == movie_id).first()


def list_movies(db: Session, genre: str | None = None, year: int | None = None) -> list[Movie]:
    query = db.query(Movie)
    if genre:
        query = query.filter(Movie.genre == genre)
    if year:
        query = query.filter(Movie.release_year == year)
    return query.all()


def create_movie(db: Session, movie_data: MovieCreate, created_by: uuid.UUID, video_file_id: str | None, video_size_bytes: int | None) -> Movie:
    new_movie = Movie(
        **movie_data.model_dump(),
        created_by=created_by,
        video_file_id=video_file_id,
        video_size_bytes=video_size_bytes,
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie


def update_movie(db: Session, movie_id: uuid.UUID, movie_data: MovieCreate) -> Movie | None:
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        return None
    for field, value in movie_data.model_dump().items():
        setattr(movie, field, value)
    db.commit()
    db.refresh(movie)
    return movie


def delete_movie(db: Session, movie_id: uuid.UUID) -> bool:
    movie = get_movie_by_id(db, movie_id)
    if not movie:
        return False

    if movie.video_file_id:
        delete_movie_video(movie.video_file_id)

    db.delete(movie)
    db.commit()
    return True


def get_average_rating(db: Session, movie_id: uuid.UUID) -> float | None:
    result = db.query(func.avg(Rating.rating)).filter(Rating.movie_id == movie_id).scalar()
    return round(result, 1) if result is not None else None

def approve_movie(
    db: Session,
    movie_id: uuid.UUID,
    admin_id: uuid.UUID,
):
    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()

    if movie is None:
        return None

    movie.status = MovieStatus.APPROVED
    movie.approved_by = admin_id

    db.commit()
    db.refresh(movie)

    return movie

def reject_movie(
    db: Session,
    movie_id: uuid.UUID,
):
    movie = db.query(Movie).filter(
        Movie.id == movie_id
    ).first()

    if movie is None:
        return None

    movie.status = MovieStatus.NOT_APPROVED
    movie.approved_by = None

    db.commit()
    db.refresh(movie)

    return movie