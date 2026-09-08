import os
from collections.abc import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


class Base(DeclarativeBase):  # Định nghĩa các mô hình bảng sau này
    pass


# Khởi tạo engine bất đồng bộ và bộ tạo session (async_sessionmaker) để giao tiếp với DB
# expire_on_commit=False giúp dữ liệu không bị xoá khỏi bộ nhớ tạm sau khi commit
engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    import Category.models
    import Image.models
    import Comment.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Hàm Dependency Generator cấp phát và đóng kết nối session cho từng request một cách an toàn.
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
