import uuid

from sqlalchemy.orm import Session

from app.models.rating_model import Rating
from app.models.movie_model import Movie
from app.schemas.rating_schema import RatingCreate


def create_rating(db: Session, movie_id: uuid.UUID, user_id: uuid.UUID, rating_data: RatingCreate):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return "not_found"

    existing = (
        db.query(Rating)
        .filter(Rating.movie_id == movie_id, Rating.user_id == user_id)
        .first()
    )
    if existing:
        return "duplicate"

    new_rating = Rating(movie_id=movie_id, user_id=user_id, **rating_data.model_dump())
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    return new_rating


def list_ratings_for_movie(db: Session, movie_id: uuid.UUID) -> list[Rating]:
    return db.query(Rating).filter(Rating.movie_id == movie_id).all()


def update_rating(db: Session, rating_id: uuid.UUID, user_id: uuid.UUID, rating_data: RatingCreate):
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        return "not_found"
    if rating.user_id != user_id:
        return "forbidden"

    rating.rating = rating_data.rating
    rating.review = rating_data.review
    db.commit()
    db.refresh(rating)
    return rating


def delete_rating(db: Session, rating_id: uuid.UUID, user_id: uuid.UUID) -> str:
    rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        return "not_found"
    if rating.user_id != user_id:
        return "forbidden"

    db.delete(rating)
    db.commit()
    return "success"


def list_ratings_by_user(db: Session, user_id: uuid.UUID) -> list[Rating]:
    return db.query(Rating).filter(Rating.user_id == user_id).all()