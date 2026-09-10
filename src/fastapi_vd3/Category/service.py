import uuid
import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sql_delete
from Category.models import Category
from Category.schemas import CategoryCreate
from Image.models import Image
from Comment.models import Comment


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
    result = await session.execute(select(Image).where(Image.category_id == category.id))
    images = result.scalars().all()
    image_ids = [image.id for image in images]

    if image_ids:
        await session.execute(sql_delete(Comment).where(Comment.image_id.in_(image_ids)))
        for image in images:
            if image.file_path and os.path.exists(image.file_path):
                os.remove(image.file_path)
        await session.execute(sql_delete(Image).where(Image.id.in_(image_ids)))

    await session.delete(category)
    await session.commit()

async def update_category(category: Category, category_create: CategoryCreate, session: AsyncSession):
    category.name = category_create.name
    category.description = category_create.description
    await session.commit()
    await session.refresh(category)
    return category