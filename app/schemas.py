from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class ImageUpdate(BaseModel):
    caption: str | None = None


class ImageResponse(BaseModel):
    id: UUID
    file_name: str
    file_path: str
    caption: str | None
    created_at: datetime

    # Pydantic tự động chuyển đổi dữ liệu từ mô hình SQLAlchemy sang dạng JSON
    model_config = ConfigDict(from_attributes=True)


class ImagePut(BaseModel):
    caption: str | None = None
    file_name: str | None = None


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: UUID
    image_id: UUID
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
