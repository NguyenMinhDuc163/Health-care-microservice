# Sử dụng Python 3.11 làm base image
FROM python:3.11-slim

# Thiết lập biến môi trường
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies hệ thống
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Sao chép requirements.txt
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ project
COPY . .

# Tạo script để chạy migrations và khởi động server
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
python manage.py runserver 0.0.0.0:8002\n\
' > /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

# Expose port 8002
EXPOSE 8002

# Chạy entrypoint script
CMD ["/app/entrypoint.sh"] 