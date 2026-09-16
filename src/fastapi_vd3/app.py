import os
import time
import sentry_sdk
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path as FilePath

from db import create_db_and_tables, async_session_maker
from auth.views import router as auth_router
from Category.views import router as category_router
from Image.views import router as image_router
from Comment.views import router as comment_router
from fastapi.middleware.cors import CORSMiddleware

sentry_dns = os.getenv("SENTRY_DSN")
if sentry_dns:
    sentry_sdk.init(dsn=sentry_dns, traces_sample_rate=1.0)

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

# Cấu hình CORS
# CORS (Cross-Origin Resource Sharing) quyết định trình duyệt có cho phép
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"], #cho phép frontend truy cập
    allow_credentials=True,     # Cho phép request kèm cookie / Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phục vụ các file tĩnh (ảnh đã lưu) thông qua đường dẫn URL
app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="static")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):  # Middleware đo hiệu năng: chạy quanh mọi request đi qua app.
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s" 
    print(
        f"Request: {request.method} {request.url.path} completed in {process_time:.4f}s")
    return response


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):   # Mở 1 phiên (session) kết nối DB riêng cho mỗi request, rồi tự đóng lại khi request xử lý xong
    async with async_session_maker() as session:
        request.state.db = session
        response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):   # Bắt tất cả exception không được xử lý
    if sentry_dns:
        sentry_sdk.capture_exception(exc) #gửi lỗi lên sentry
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Đã xảy ra lỗi nội bộ. Vui lòng thử lại sau.", "error": str(exc)},
    )

app.include_router(auth_router)
app.include_router(category_router)
app.include_router(image_router)
app.include_router(comment_router)
