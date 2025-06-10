FROM python:3.13-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Cài đặt wait-for-it và psql
RUN apt-get update && apt-get install -y wget postgresql-client && \
    wget https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh && \
    chmod +x wait-for-it.sh

# Expose port 8003
EXPOSE 8003

# Script để tạo database và chạy migrations
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Chạy entrypoint script
CMD ["/entrypoint.sh"] 