import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class Image(Base):
    __tablename__ = "image_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String)
    saved_file_name: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    caption: Mapped[str | None] = mapped_column(Text, default=None)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)

    comments: Mapped[list["Comment"]] = relationship(
        # quan hệ 1-n với bảng Comment
        "Comment", back_populates="image", cascade="all, delete-orphan")
    category: Mapped["Category | None"] = relationship(
        "Category", back_populates="images")  # quan hệ n-1 với bảng Category
