from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

class RatingCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    review: str | None = None

class RatingResponse(BaseModel):
    id: uuid.UUID
    rating: int
    review: str | None
    created_at: datetime
    updated_at: datetime
    movie_id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)
