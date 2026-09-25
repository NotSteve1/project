from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
import uuid

class MovieCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    genre: str = Field(min_length=1, max_length=150)
    release_year: int = Field(ge=1888, le=2100)

class MovieResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_by: uuid.UUID
    description: str
    genre: str
    average_rating: float | None = None
    created_at: datetime
    updated_at: datetime
    release_year: int  
    video_url: str | None = None  

    model_config = ConfigDict(from_attributes=True)
