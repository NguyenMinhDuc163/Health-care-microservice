docker build -t patient-service .

docker run -d \
  --name patient-service \
  -p 8000:8000 \
  -e DB_NAME=patient_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=NguyenDuc@163 \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5432 \
  patient-service

docker run -d `
  --name patient-service `
  -p 8000:8000 `
  -e DB_NAME=patient_db `
  -e DB_USER=postgres `
  -e DB_PASSWORD=NguyenDuc@163 `
  -e DB_HOST=host.docker.internal `
  -e DB_PORT=5432 `
  --add-host=host.docker.internal:host-gateway `
  patient-service