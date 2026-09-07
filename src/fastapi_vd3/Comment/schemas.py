from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CommentCreate(BaseModel):
    user_name: str | None = "Anonymous"
    content: str


class CommentResponse(BaseModel):
    id: UUID
    image_id: UUID
    user_name: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)