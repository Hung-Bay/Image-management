import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db import get_async_session
from Image.service import get_image_by_id
from Comment import service
from Comment.schemas import CommentCreate, CommentResponse
from auth.utils import get_current_user
from auth.models import User


router = APIRouter(tags=["Comments"])


@router.get("/images/{image_id}/comments", response_model=list[CommentResponse])
async def get_comment(image_id: uuid.UUID, session: AsyncSession = Depends(get_async_session)):
    image = await service.get_image_by_id(image_id, session)
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho")
    return await service.get_comments_by_image_id(image.id, session)


@router.post("/images/{image_id}/comments", response_model=CommentResponse)
async def create_comment(image_id: uuid.UUID, comment: CommentCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    image = await get_image_by_id(image_id, session)
    if not image:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy ảnh với ID đã cho")
    comment.user_name = current_user.username
    new_comment = await service.create_comment(comment, image_id, session)
    return new_comment


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: uuid.UUID, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    comment = await service.get_comments_by_id(comment_id, session)
    if not comment:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy bình luận với ID đã cho")
    if current_user.role != "admin" and comment.user_name != current_user.username:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa bình luận này")
    await service.delete_comment(comment, session)
    return {"message": "Bình luận đã được xóa thành công."}


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: uuid.UUID, updated_comment: CommentCreate, session: AsyncSession = Depends(get_async_session), current_user: User = Depends(get_current_user)):
    comment = await service.get_comments_by_id(comment_id, session)
    if not comment:
        raise HTTPException(
            status_code=404, detail="Không tìm thấy bình luận với ID đã cho")
    if current_user.role != "admin" and comment.user_name != current_user.username:
        raise HTTPException(status_code=403, detail="Bạn không có quyền sửa bình luận này")
    updated_comment = await service.update_comment(comment, updated_comment, session)
    return updated_comment
