from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ImageUpdate(BaseModel):
    caption: str | None = None


class ImageResponse(BaseModel):
    id: UUID
    user_id: UUID
    file_name: str
    saved_file_name: str
    file_path: str
    caption: str | None
    likes_count: int
    created_at: datetime

    # Pydantic tự động chuyển đổi dữ liệu từ mô hình SQLAlchemy sang dạng JSON
    model_config = ConfigDict(from_attributes=True)


class ImagePut(BaseModel):
    caption: str | None = None
    file_name: str | None = None
