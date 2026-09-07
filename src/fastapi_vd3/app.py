import os
import shutil
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path as FilePath
from db import get_async_session, create_db_and_tables
from model import Image, Comment, Category
from schemas import ImageUpdate, ImageResponse, ImagePut, CommentCreate, CommentResponse, CategoryCreate, CategoryResponse

PACKAGE_DIR = FilePath(__file__).resolve().parent

# 2. Tạo đường dẫn tuyệt đối tới src/fastapi_vd3/static/uploads
UPLOAD_DIR = PACKAGE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)  # tạo thư mục để chứa ảnh


# Hàm context manager bất đồng bộ để quản lý vòng đời của ứng dụng FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)  # khởi tạo bảng khi ứng dụng vừa chạy

# Phục vụ các file tĩnh (ảnh đã lưu) thông qua đường dẫn URL
app.mount("/static", StaticFiles(directory="static"), name="static")


# ===========================================CATEGORIES==========================================

@app.post("/categories", response_model=CategoryResponse)
async def create_category(category_create: CategoryCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Category).where(Category.name == category_create.name)
    result = await session.execute(stmt)
    existing_category = result.scalar_one_or_none()
    if existing_category:
        raise HTTPException(
            status_code=400, detail="Danh mục với tên này đã tồn tại.")
    new_category = Category(name=category_create.name,
                            description=category_create.description)
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category


@app.get("/categories", response_model=list[CategoryResponse])
async def get_all_categories(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Category).order_by(Category.created_at.desc())
    result = await session.execute(stmt)
    categories = result.scalars().all()
    return categories


@app.get("/categories/{category_id}/images", response_model=list[ImageResponse])
async def get_images_by_category(category_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    stmt = select(Image).where(Image.category_id ==
                               category_id).order_by(Image.created_at.desc())
    result1 = await session.execute(stmt)
    images = result1.scalars().all()
    return images


@app.delete("/categories/{category_id}")
async def delete_category(category_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    await session.delete(category)
    await session.commit()
    return {"message": "Danh mục đã được xóa thành công.", "category_id": str(category_id)}


@app.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: uuid.UUID, category_create: CategoryCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    category.name = category_create.name
    category.description = category_create.description
    await session.commit()
    await session.refresh(category)
    return category


# ===========================================IMAGES==========================================

@app.post("/images", response_model=ImageResponse)
async def upload_image(file: UploadFile = File(...), category_id: uuid.UUID | None = Form(None), caption: str | None = Form(None), session: AsyncSession = Depends(get_async_session)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400, detail="File gửi lên phải là ảnh.")
    if category_id:
        stmt = select(Category).where(Category.id == category_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        if not category:
            raise HTTPException(
                status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")

    extension = os.path.splitext(file.filename)[1]  # lấy phần mở rộng của tệp
    saved_file_name = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_file_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)  # Lưu tệp vật lý vào đĩa

    new_image = Image(category_id=category_id, file_name=file.filename, saved_file_name=saved_file_name,
                      file_path=file_path, caption=caption)
    session.add(new_image)
    await session.commit()
    await session.refresh(new_image)

    return new_image


@app.get("/images", response_model=list[ImageResponse])
async def get_all_images(session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).order_by(Image.created_at.desc())
    result = await session.execute(stmt)
    images = result.scalars().all()
    return images


@app.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")
    return image


@app.patch("/images/{image_id}", response_model=ImageResponse)
async def update_image_caption(image_id: uuid.UUID, image_update: ImageUpdate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")

    if image_update.caption is not None:
        image.caption = image_update.caption

    await session.commit()
    await session.refresh(image)
    return image


@app.delete("/images/{image_id}")
async def delete_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")
    if os.path.exists(image.file_path):
        os.remove(image.file_path)

    await session.delete(image)
    await session.commit()
    return {"message": "Ảnh đã được xóa thành công.", "image_id": str(image_id)}


@app.put("/images/{image_id}")
async def replace_image_inf(image_id: uuid.UUID, image_put: ImagePut, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho")
    image.caption = image_put.caption
    image.file_name = image_put.file_name
    await session.commit()
    await session.refresh(image)
    return image


# ===========================================COMMENTS==========================================

@app.post("/images/{image_id}/comments", response_model=CommentResponse)
async def add_comment(image_id: uuid.UUID, comment_create: CommentCreate, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")
    new_comment = Comment(
        image_id=image_id, user_name=comment_create.user_name, content=comment_create.content)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment


@app.get("/images/{image_id}/comments", response_model=list[CommentResponse])
async def get_comments(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Image).where(Image.id == image_id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")
    stmt = select(Comment).where(Comment.image_id ==
                                 image_id).order_by(Comment.created_at.desc())
    result1 = await session.execute(stmt)
    comments = result1.scalars().all()
    return comments


@app.delete("/comments/{comment_id}")
async def delete_comment(comment_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy bình luận với ID đã cho.")
    await session.delete(comment)
    await session.commit()
    return {"message": "Bình luận đã được xóa thành công.", "comment_id": str(comment_id)}


@app.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: uuid.UUID, comment_create: CommentCreate, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy bình luận với ID đã cho.")
    comment.content = comment_create.content
    await session.commit()
    await session.refresh(comment)
    return comment


# ===========================================LIKES==========================================

@app.post("/images/{image_id}/like", response_model=ImageResponse)
async def like_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")

    image.likes_count += 1  # Tăng số lượt thích lên 1
    await session.commit()
    await session.refresh(image)
    return image


@app.post("/images/{image_id}/unlike", response_model=ImageResponse)
async def unlike_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho.")

    if image.likes_count > 0:
        image.likes_count -= 1  # Giảm số lượt thích xuống 1
    await session.commit()
    await session.refresh(image)
    return image
