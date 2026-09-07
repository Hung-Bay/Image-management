import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Category.models import Category
from Category.schemas import CategoryCreate
from Image.models import Image


async def get_category_by_name(name: str, session: AsyncSession):
    stmt = select(Category).where(Category.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def get_category_by_id(category_id: uuid.UUID, session: AsyncSession):
    stmt = select(Category).where(Category.id == category_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

async def create_category(category_create: CategoryCreate, session: AsyncSession):
    new_category = Category(
        name=category_create.name,
        description=category_create.description
    )
    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)
    return new_category

async def get_all_categories(session: AsyncSession):
    stmt = select(Category).order_by(Category.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()

async def delete_category(category: Category, session: AsyncSession):
    # Xóa tất cả các hình ảnh liên quan đến danh mục
    for image in category.images:
        await session.delete(image)

    # Xóa danh mục
    await session.delete(category)
    await session.commit()

async def update_category(category: Category, category_create: CategoryCreate, session: AsyncSession):
    category.name = category_create.name
    category.description = category_create.description
    await session.commit()
    await session.refresh(category)
    return category