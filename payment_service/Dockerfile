# Sử dụng Python 3.11 làm base image
FROM python:3.11-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Expose port 8006
EXPOSE 8006

# Tạo script khởi động
RUN echo '#!/bin/bash\n\
python manage.py migrate\n\
gunicorn --bind 0.0.0.0:8006 payment_service.wsgi:application' > /app/start.sh && \
chmod +x /app/start.sh

# Chạy script khởi động
CMD ["/app/start.sh"] 