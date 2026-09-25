from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.user_model import User
from app.schemas.movie_schema import MovieResponse
from app.services import movie_service
from app.utils.dependencies import require_admin
from app.models.movie_model import MovieStatus


router = APIRouter(
    prefix="/admin/movies",
    tags=["Movie Status"],
)

@router.get("/pending", response_model=list[MovieResponse])
def get_pending_movies(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return movie_service.get_pending_movies(db)

@router.patch("/{movie_id}/approve", response_model=MovieResponse)
def approve_movie(
    movie_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    movie = movie_service.get_movie(
        db,
        movie_id,
    )

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    if movie.status != MovieStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Movie has already been reviewed",
        )
    

    return movie_service.approve_movie(
        db,
        movie,
        admin.id,
    )

@router.patch("/{movie_id}/reject", response_model=MovieResponse)
def reject_movie(
    movie_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    movie = movie_service.get_movie(
        db,
        movie_id,
    )

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found",
        )

    if movie.status != MovieStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Movie has already been reviewed",
        )

    return movie_service.reject_movie(
        db,
        movie,
    )