FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tạo thư mục logs nếu chưa tồn tại
RUN mkdir -p /app/logs

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"] 