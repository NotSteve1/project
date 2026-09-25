from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
import uuid
from app.database.db import get_db
from app.schemas.movie_schema import MovieResponse, MovieCreate
from app.services import movie_service
from app.models.user_model import User
from app.core.api_storage import get_video_download_url, upload_movie_video
from app.utils.dependencies import get_current_user
from sqlalchemy.orm import Session

router = APIRouter(prefix="/movies", tags=["Movies"])


def build_movie_response(movie) -> MovieResponse:
    video_url = get_video_download_url(movie.video_file_id) if movie.video_file_id else None
    return MovieResponse(
        id=movie.id,
        title=movie.title,
        description=movie.description,
        genre=movie.genre,
        release_year=movie.release_year,
        status=movie.status,
        created_by=movie.created_by,
        approved_by=movie.approved_by,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
        video_url=video_url,
    )


@router.post("/", response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
def post_movie(
    title: str = Form(...),
    description: str | None = Form(None),
    genre: str = Form(...),
    release_year: int = Form(...),
    video: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    video_file_id, video_size = (None, None)
    if video:
        video_file_id, video_size = upload_movie_video(video)

    movie_data = MovieCreate(title=title, description=description, genre=genre, release_year=release_year)
    movie = movie_service.create_movie(db, movie_data, current_user.id, video_file_id, video_size)
    return build_movie_response(movie)


@router.get("/", response_model=list[MovieResponse])
def list_all_movies(db: Session = Depends(get_db), genre: str | None = None, year: str | None = None):
    movie_list = movie_service.list_movies(db, genre, year)
    return [build_movie_response(m) for m in movie_list]


@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: uuid.UUID, db: Session = Depends(get_db)):
    movie = movie_service.get_movie_by_id(db, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return build_movie_response(movie)


@router.patch("/{movie_id}", response_model=MovieResponse)
def patch_movie(movie_id: uuid.UUID, movie_data: MovieCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    up_movie = movie_service.update_movie(db, movie_id, movie_data)
    if not up_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return build_movie_response(up_movie)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie(movie_id: uuid.UUID, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    del_movie = movie_service.delete_movie(db, movie_id)
    if not del_movie:
        raise HTTPException(status_code=404, detail="Movie not found")