import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Comment.models import Comment
from Comment.schemas import CommentCreate
from Image.models import Image


async def get_image_by_id(image_id: uuid.UUID, session: AsyncSession):
    stmt = select(Image).where(Image.id == image_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_comments_by_id(comment_id: uuid.UUID, session: AsyncSession):
    stmt = select(Comment).where(Comment.id == comment_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_comments_by_image_id(image_id: uuid.UUID, session: AsyncSession):
    stmt = select(Comment).where(Comment.image_id == image_id)
    result = await session.execute(stmt)
    return result.scalars().all()


async def create_comment(comment: CommentCreate, image_id: uuid.UUID, session: AsyncSession):
    new_comment = Comment(
        image_id=image_id,
        user_name=comment.user_name,
        content=comment.content
    )
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment


async def delete_comment(comment: Comment, session: AsyncSession):
    await session.delete(comment)
    await session.commit()


async def update_comment(comment: Comment, updated_comment: CommentCreate, session: AsyncSession):
    comment.content = updated_comment.content
    await session.commit()
    await session.refresh(comment)
    return comment
