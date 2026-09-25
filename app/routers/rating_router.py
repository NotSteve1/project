import uuid
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dependencies import get_current_user
from app.database.db import get_db
from app.services.rating_service import create_rating, delete_rating, list_ratings_by_user, list_ratings_for_movie, update_rating
from app.models.user_model import User
from app.schemas.rating_schema import RatingCreate, RatingResponse

router = APIRouter(prefix="/ratings", tags=["Ratings"])

@router.get("/users/{user_id}/ratings", response_model=list[RatingResponse])
def list_User_ratings(user_id: uuid.UUID, db: Session = Depends(get_db)):
    list_movie = list_ratings_by_user(db, user_id.id)

    return list_movie

@router.post("/movie_id/{movie_id}/ratings", response_model=RatingResponse,status_code=status.HTTP_201_CREATED)
def create_movie_rate(movie_id: uuid.UUID, rating_data: RatingCreate, db: Session = Depends(get_db), user_id: User = Depends(get_current_user)):
    rate = create_rating(db, movie_id, user_id.id, rating_data)

    if rate == "not_found":
        raise HTTPException(status_code=404, detail="Movie not found")
    if rate == "forbidden":
        raise HTTPException(status_code=409, detail="You already rated this movie")
    return rate

@router.get("/movie/{movie_id}/ratings", response_model=list[RatingResponse])
def list_movie_ratings(movie_id: uuid.UUID, db: Session = Depends(get_db)):
    result = list_ratings_for_movie(db, movie_id)
    return result

@router.patch("/ratings/{rating_id}", response_model=RatingResponse)
def update_rate(rating_id: uuid.UUID, rating_data: RatingCreate, db: Session = Depends(get_db), user_id: User = Depends(get_current_user)):
    result = update_rating(db, rating_id, user_id.id, rating_data)

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Movie not found")
    if result == "forbidden":
        raise HTTPException(status_code=403, detail="Not your rating")
    return result

@router.delete("/ratings/{rating_id}", response_model=RatingCreate)
def delete_rate(rating_id: uuid.UUID, user_id: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = delete_rating(db, rating_id, user_id.id)

    if result == "not_found":
        raise HTTPException(status_code=404, detail="Movie not found")
    if result == "forbidden":
        raise HTTPException(status_code=403, detail="Not your rating")