docker run -d `
  --name booking-service`
  -p 8003:8003 `
  -e DB_NAME=booking_db `
  -e DB_USER=postgres `
  -e DB_PASSWORD=NguyenDuc@163 `
  -e DB_HOST=host.docker.internal `
  -e DB_PORT=5432 `
  --add-host=host.docker.internal:host-gateway `
  booking-service