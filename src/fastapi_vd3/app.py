import os
import shutil
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path as FilePath
from db import create_db_and_tables
from Category.views import router as category_router
from Image.views import router as image_router
from Comment.views import router as comment_router

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
app.mount("/static", StaticFiles(directory=str(UPLOAD_DIR)), name="static")

app.include_router(category_router)
app.include_router(image_router)
app.include_router(comment_router)