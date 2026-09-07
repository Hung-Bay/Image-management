import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_async_session
from Category.service import get_category_by_id
from Image import service
from Image.schemas import ImageResponse, ImageUpdate, ImagePut

router = APIRouter(prefix="/images", tags=["Images"])


@router.post("/", response_model=ImageResponse)
async def upload_image(
    file: UploadFile = File(...),
    category_id: uuid.UUID | None = Form(None),
    caption: str | None = Form(None),
    session: AsyncSession = Depends(get_async_session)
):
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=400, detail="Định dạng file sai, chỉ cho phép JPEG, PNG và GIF.")
    if category_id is not None:
        category = await get_category_by_id(category_id, session)
        if category is None:
            raise HTTPException(
                status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")

    new_image = await service.save_uploaded_file(file, category_id, caption, session)
    return new_image


@router.get("/", response_model=list[ImageResponse])
async def get_all_images(session: AsyncSession = Depends(get_async_session)):
    images = await service.get_all_images(session)
    return images


@router.get("/{image_id}", response_model=ImageResponse)
async def get_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if image is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hình ảnh với ID đã cho.")
    return image


@router.put("/{image_id}", response_model=ImageResponse)
async def update_image(image_id: uuid.UUID, image_update: ImageUpdate, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if image is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hình ảnh với ID đã cho.")
    updated_image = await service.update_image(image, image_update, session)
    return updated_image


@router.delete("/{image_id}", response_model=dict)
async def delete_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if image is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hình ảnh với ID đã cho.")
    await service.delete_image(image, session)
    return {"message": "Hình ảnh đã được xóa thành công."}


@router.post("/{image_id}/like", response_model=ImageResponse)
async def like_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if image is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hình ảnh với ID đã cho.")
    return await service.increment_likes_count(image, session)


@router.post("/{image_id}/unlike", response_model=ImageResponse)
async def unlike_image(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if image is None:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy hình ảnh với ID đã cho.")
    return await service.decrement_likes_count(image, session)
