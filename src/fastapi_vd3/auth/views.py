import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt, JWTError

from db import get_async_session
from auth.models import User
from auth.schemas import LoginRequest, RefreshRequest, TokenResponse, RegisterRequest, UserResponse
from auth.utils import verify_password, get_password_hash, create_tokens, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login(login_request: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    stmt = select(User).where(User.username == login_request.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None or not verify_password(login_request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tên đăng nhập hoặc mật khẩu không đúng.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = create_tokens(str(user.id), user.role)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type="bearer", username=user.username, role=user.role, user_id=str(user.id))

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_request: RefreshRequest, session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token làm mới không hợp lệ.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise credentials_exception

        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception

        user_id = uuid.UUID(user_id_str)

    except JWTError:
        raise credentials_exception

    stmt = select(User).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Người dùng không tồn tại.")

    new_access_token, _ = create_tokens(str(user.id), user.role)
    return TokenResponse(access_token=new_access_token, refresh_token=refresh_request.refresh_token)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(register_request: RegisterRequest, session: AsyncSession = Depends(get_async_session)):
    stmt = select(User).where((User.username == register_request.username) | (User.email == register_request.email))
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập hoặc email đã tồn tại.",
        )

    hashed_password = get_password_hash(register_request.password)
    new_user = User(
        username=register_request.username,
        email=register_request.email,
        hashed_password=hashed_password,
        role="user"
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserResponse(
        id=str(new_user.id),
        username=new_user.username,
        email=new_user.email,
        role=new_user.role
    )