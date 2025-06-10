# Sử dụng Python 3.13 làm base image
FROM python:3.13-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies hệ thống
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code và file .env vào container
COPY . .

# Tạo script khởi động
RUN echo '#!/bin/bash\n\
echo "Waiting for postgres..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate\n\
\n\
echo "Starting server..."\n\
python manage.py runserver 0.0.0.0:8000' > /app/entrypoint.sh

# Cài đặt netcat để kiểm tra kết nối database
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Cấp quyền thực thi cho script
RUN chmod +x /app/entrypoint.sh

# Expose port 8000
EXPOSE 8000

# Sử dụng script khởi động
CMD ["/app/entrypoint.sh"] 