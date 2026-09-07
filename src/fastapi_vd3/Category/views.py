import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_async_session
from Category import service
from Category.schemas import CategoryCreate, CategoryResponse
from Image.schemas import ImageResponse


router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
async def create_category(category_create: CategoryCreate, session: AsyncSession = Depends(get_async_session)):
    existing_category = await service.get_category_by_name(category_create.name, session)
    if existing_category:
        raise HTTPException(status_code=400, detail="Danh mục đã tồn tại.")
    new_category = await service.create_category(category_create, session)
    return new_category

@router.get("/", response_model=list[CategoryResponse])
async def get_all_categories(session: AsyncSession = Depends(get_async_session)):
    categories = await service.get_all_categories(session)
    return categories

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    category = await service.get_category_by_id(category_id, session)
    if category is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    return await service.get_category_by_id(category_id, session)

@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    category = await service.get_category_by_id(category_id, session)
    if category is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    await service.delete_category(category, session)
    return {"message": "Danh mục và các hình ảnh liên quan đã được xóa thành công."}

@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: uuid.UUID, category_update: CategoryCreate, session: AsyncSession = Depends(get_async_session)):
    category = await service.get_category_by_id(category_id, session)
    if category is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy danh mục với ID đã cho.")
    updated_category = await service.update_category(category, category_update, session)
    return updated_category