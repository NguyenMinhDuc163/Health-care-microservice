#!/bin/bash

# Chờ PostgreSQL sẵn sàng
./wait-for-it.sh postgres:5432 -- echo "PostgreSQL is up"

# Tạo database nếu chưa tồn tại
PGPASSWORD=$DB_PASSWORD psql -h postgres -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
PGPASSWORD=$DB_PASSWORD psql -h postgres -U postgres -c "CREATE DATABASE $DB_NAME"

# Chạy migrations
python manage.py migrate

# Khởi động server
python manage.py runserver 0.0.0.0:8003 