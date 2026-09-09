import os
import uuid
import shutil
from fastapi import UploadFile
from pathlib import Path as FilePath
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Image.models import Image
from Image.schemas import ImageUpdate, ImageResponse, ImagePut

PACKAGE_DIR = FilePath(__file__).resolve().parent.parent
UPLOAD_DIR = PACKAGE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


async def get_image_by_id(image_id: uuid.UUID, session: AsyncSession):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_images(session: AsyncSession):
    stmt = select(Image).order_by(Image.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def save_uploaded_file(upload_file: UploadFile, category_id: uuid.UUID | None, caption: str | None, user_id: uuid.UUID, session: AsyncSession):
    file_extension = os.path.splitext(upload_file.filename)[1]
    save_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, save_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    new_image = Image(
        category_id=category_id,
        user_id=user_id,
        file_name=upload_file.filename,
        saved_file_name=save_filename,
        file_path=str(file_path),
        caption=caption,
    )
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)
    return new_image


async def update_image(image: Image, image_update: ImageUpdate, session: AsyncSession):
    if image_update.caption is not None:
        image.caption = image_update.caption
    await session.commit()
    await session.refresh(image)
    return image


async def update_image_put(image: Image, image_put: ImagePut, session: AsyncSession):
    if image_put.caption is not None:
        image.caption = image_put.caption
    if image_put.file_name is not None:
        image.file_name = image_put.file_name
    await session.commit()
    await session.refresh(image)
    return image


async def delete_image(image: Image, session: AsyncSession):
    # Xóa file ảnh khỏi hệ thống tệp
    if os.path.exists(image.file_path):
        os.remove(image.file_path)

    # Xóa bản ghi ảnh khỏi cơ sở dữ liệu
    await session.delete(image)
    await session.commit()


async def increment_likes_count(image: Image, session: AsyncSession):
    image.likes_count += 1
    await session.commit()
    await session.refresh(image)
    return image


async def decrement_likes_count(image: Image, session: AsyncSession):
    if image.likes_count > 0:
        image.likes_count -= 1
    await session.commit()
    await session.refresh(image)
    return image
