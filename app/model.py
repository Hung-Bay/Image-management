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
    file_name: Mapped[str] = mapped_column(String)
    saved_file_name: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    caption: Mapped[str | None] = mapped_column(Text, default=None)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)

    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="image", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("image_posts.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now)

    image: Mapped["Image"] = relationship("Image", back_populates="comments")
