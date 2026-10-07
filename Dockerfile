FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY alembic ./alembic
COPY src ./src

# User không phải root + thư mục upload (volume sẽ thừa hưởng quyền sở hữu này)
RUN useradd --create-home app \
    && mkdir -p /app/src/fastapi_vd3/static/uploads \
    && chown -R app:app /app
USER app

# Các import trong code (from db import ..., app:app) tính từ thư mục này
WORKDIR /app/src/fastapi_vd3

EXPOSE 8000

# 0.0.0.0 để nginx (container khác) gọi được; cổng 8000 KHÔNG publish ra máy host
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]