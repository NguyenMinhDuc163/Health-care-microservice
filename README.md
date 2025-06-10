# Hệ Thống Quản Lý Y Tế - Healthcare Microservice

## 📋 Mô Tả Dự Án

Đây là một hệ thống quản lý y tế hiện đại được xây dựng theo kiến trúc microservice, tích hợp chatbot AI để hỗ trợ tư vấn y tế. Hệ thống cung cấp các chức năng toàn diện từ quản lý bệnh nhân, đặt lịch khám, quản lý thuốc đến thanh toán và tư vấn AI.

## 🏗️ Kiến Trúc Hệ Thống

Hệ thống được thiết kế theo mô hình **Microservice Architecture** với các service độc lập:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Gateway      │    │   Auth Service  │
│   (React/Vue)   │────│   (Port 8080)   │────│   (Port 8001)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼────────┐
        │Patient Service│ │Booking Serv.│ │Chatbot Serv. │
        │  (Port 8002) │ │ (Port 8003) │ │ (Port 8009)  │
        └──────────────┘ └─────────────┘ └──────────────┘
                │               │               │
        ┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼────────┐
        │Pharmacy Serv.│ │Clinical Serv│ │Payment Serv. │
        │  (Port 8004) │ │ (Port 8005) │ │ (Port 8006)  │
        └──────────────┘ └─────────────┘ └──────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                │
                    ┌───────────▼───────────┐
                    │     Databases        │
                    │ PostgreSQL + MySQL   │
                    └─────────────────────┘
```

## 🚀 Các Service và Chức Năng

### 1. **Gateway Service** (Port 8080)
- **Chức năng**: API Gateway, định tuyến request đến các service phù hợp
- **Tính năng**: Load balancing, Authentication middleware, Rate limiting

### 2. **Auth Service** (Port 8001)
- **Chức năng**: Quản lý xác thực và phân quyền người dùng
- **Tính năng**:
  - Đăng ký tài khoản (PATIENT, DOCTOR, ADMIN)
  - Đăng nhập/Đăng xuất
  - JWT Token management (Access/Refresh token)
  - Phân quyền theo vai trò
  - Quản lý thông tin profile người dùng

### 3. **Patient Service** (Port 8002)
- **Chức năng**: Quản lý thông tin bệnh nhân và hồ sơ y tế
- **Tính năng**:
  - CRUD thông tin bệnh nhân (họ tên, ngày sinh, địa chỉ, CMND, v.v.)
  - Quản lý hồ sơ bệnh án (Medical Records)
  - Lưu trữ tiền sử bệnh, dị ứng, nhóm máu
  - Tìm kiếm bệnh nhân theo tên
  - Quản lý trạng thái điều trị

### 4. **Chatbot Service** (Port 8009)
- **Chức năng**: Tư vấn y tế thông minh bằng AI
- **Tính năng**:
  - Chat với AI để tư vấn triệu chứng
  - Gợi ý chẩn đoán sơ bộ
  - Hướng dẫn sơ cứu cơ bản
  - Tư vấn thuốc và liều dùng

### 5. **Booking Service** (Port 8003)
- **Chức năng**: Quản lý lịch hẹn khám bệnh
- **Tính năng**:
  - Đặt lịch khám với bác sĩ
  - Xem danh sách lịch hẹn
  - Cập nhật trạng thái lịch hẹn (pending, confirmed, completed, cancelled)
  - Ghi chú yêu cầu đặc biệt

### 6. **Pharmacy Service** (Port 8004)
- **Chức năng**: Quản lý kho thuốc và dược phẩm
- **Tính năng**:
  - CRUD thông tin thuốc (tên, mô tả, giá, số lượng)
  - Quản lý nhà sản xuất và hạn sử dụng
  - Theo dõi tồn kho
  - Cập nhật giá thuốc

### 7. **Clinical Service** (Port 8005)
- **Chức năng**: Quản lý đơn thuốc và kê đơn
- **Tính năng**:
  - Tạo đơn thuốc cho bệnh nhân
  - Kết nối với hồ sơ bệnh án
  - Ghi chú liều dùng và cách sử dụng
  - Theo dõi tình trạng kê đơn

### 8. **Payment Service** (Port 8006)
- **Chức năng**: Xử lý thanh toán viện phí
- **Tính năng**:
  - Tính toán chi phí điều trị
  - Quản lý hóa đơn
  - Xử lý thanh toán (PENDING, COMPLETED, FAILED)
  - Phê duyệt thanh toán

## 💾 Cơ Sở Dữ Liệu

### PostgreSQL (Port 5432)
Quản lý các database:
- `auth_db` - Thông tin người dùng và xác thực
- `patient_db` - Dữ liệu bệnh nhân và hồ sơ y tế
- `booking_db` - Lịch hẹn khám bệnh
- `pharmacy_db` - Kho thuốc và dược phẩm
- `clinical_db` - Đơn thuốc và kê đơn
- `payment_db` - Thanh toán và hóa đơn

### MySQL (Port 3307)
- `user_service` - Dữ liệu bổ sung cho user service

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Django REST Framework (Python)
- **Database**: PostgreSQL 15, MySQL 5.7
- **Containerization**: Docker, Docker Compose
- **API Gateway**: Custom Django Gateway
- **Authentication**: JWT (JSON Web Tokens)
- **AI/ML**: Tích hợp chatbot AI cho tư vấn y tế
- **Documentation**: Postman Collection

## 🚀 Cài Đặt và Chạy Dự Án

### Yêu Cầu Hệ Thống
- Docker và Docker Compose
- Git
- Port 8080-8009, 5432, 3307 phải trống

### Bước 1: Clone Repository
```bash
git clone <repository-url>
cd heath_care
```

### Bước 2: Cấu Hình Environment
Kiểm tra và điều chỉnh các biến môi trường trong `docker-compose.yml`:
```yaml
environment:
  - DB_PASSWORD=
  - JWT_SECRET_KEY=your-jwt-secret-key-here
  - SECRET_KEY=django-insecure-gateway-key
```

### Bước 3: Build và Chạy Services
```bash
# Build và chạy tất cả services
docker-compose up --build

# Chạy ở chế độ nền
docker-compose up -d --build

# Xem logs
docker-compose logs -f
```

### Bước 4: Kiểm Tra Services
Truy cập các endpoint sau để kiểm tra:
- Gateway: http://localhost:8080
- Auth Service: http://localhost:8001
- Patient Service: http://localhost:8002
- Booking Service: http://localhost:8003
- Pharmacy Service: http://localhost:8004
- Clinical Service: http://localhost:8005
- Payment Service: http://localhost:8006
- Chatbot Service: http://localhost:8009

## 📚 API Documentation

### Authentication APIs
```bash
# Đăng ký tài khoản
POST /api/users/
{
  "email": "user@example.com",
  "username": "username",
  "password": "password",
  "role": "PATIENT",
  "phone": "0123456789",
  "profile": {
    "date_of_birth": "2000-01-01",
    "address": "123 ABC Street",
    "city": "Hà Nội"
  }
}

# Đăng nhập
POST /api/users/login/
{
  "email": "user@example.com",
  "password": "password"
}

# Lấy thông tin user
GET /api/users/me/
Headers: Authorization: Bearer <token>
```

### Patient Management APIs
```bash
# Tạo bệnh nhân mới
POST /api/patients/
{
  "first_name": "Nguyễn",
  "last_name": "Văn A",
  "date_of_birth": "1990-01-01",
  "gender": "M",
  "id_number": "123456789",
  "address": "123 ABC Street",
  "phone_number": "0123456789",
  "email": "patient@example.com",
  "blood_type": "A+",
  "medical_history": "Không có tiền sử bệnh",
  "allergies": "Không có dị ứng"
}

# Lấy danh sách bệnh nhân
GET /api/patients/

# Tìm kiếm bệnh nhân
GET /api/patients/?search=Nguyễn
```

### Booking APIs
```bash
# Đặt lịch khám
POST /api/appointments/
{
  "patient_id": 1,
  "doctor_id": 2,
  "appointment_date": "2024-07-01T09:00:00Z",
  "notes": "Khám tổng quát"
}

# Cập nhật trạng thái lịch hẹn
PATCH /api/appointments/1/
{
  "status": "confirmed"
}
```

### Chatbot API
```bash
# Chat với AI
POST /api/chatbot/chat/
{
  "message": "Tôi bị sốt và ho"
}
```

### Pharmacy APIs
```bash
# Thêm thuốc mới
POST /api/medicines/
{
  "name": "Paracetamol 500mg",
  "description": "Thuốc giảm đau, hạ sốt",
  "price": "25000.00",
  "quantity": 100,
  "manufacturer": "Sanofi",
  "expiry_date": "2025-12-31"
}
```

## 🔐 Phân Quyền và Bảo Mật

### Các Vai Trò (Roles)
- **PATIENT**: Bệnh nhân - Xem thông tin cá nhân, đặt lịch, chat với AI
- **DOCTOR**: Bác sĩ - Quản lý bệnh nhân, kê đơn thuốc, xem lịch khám
- **ADMIN**: Quản trị viên - Toàn quyền truy cập hệ thống

### Bảo Mật
- JWT Authentication với Access/Refresh token
- Password hashing
- API rate limiting
- CORS configuration
- Environment variables cho sensitive data

## 🧪 Testing

### Import Postman Collection
1. Mở Postman
2. Import file `docs/Heal care.postman_collection.json`
3. Thiết lập environment với biến `url=http://localhost:8080`
4. Chạy các test case theo thứ tự: Register → Login → Other APIs

### Test Scenarios
1. **Authentication Flow**: Register → Login → Access Protected APIs
2. **Patient Management**: Create → Read → Update → Delete
3. **Booking Flow**: Create Appointment → Update Status
4. **Chatbot Interaction**: Send messages and receive AI responses
5. **Payment Flow**: Create → Process → Complete

## 🔧 Troubleshooting

### Các Lỗi Thường Gặp

1. **Port đã được sử dụng**
```bash
# Kiểm tra port đang sử dụng
netstat -tulpn | grep :8080

# Thay đổi port trong docker-compose.yml
ports:
  - "8081:8080"  # Thay đổi port external
```

2. **Database connection failed**
```bash
# Kiểm tra container database
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up --build
```

3. **Service không start**
```bash
# Xem logs chi tiết
docker-compose logs <service-name>

# Rebuild service
docker-compose up --build <service-name>
```

## 🤝 Đóng Góp

1. Fork repository
2. Tạo branch mới: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -am 'Add your feature'`
4. Push branch: `git push origin feature/your-feature`
5. Tạo Pull Request

## 📝 License

Dự án này được phát hành dưới [MIT License](LICENSE).

## 👥 Tác Giả

- **Tên**: Nguyễn Minh Đức  
- **GitHub**: [@NguyenMinhDuc163](https://github.com/NguyenMinhDuc163)
- **Location**: Việt Nam 🇻🇳
- **Sponsor**: ❤️ [Support my work](https://github.com/sponsors/NguyenMinhDuc163)

[![Sponsor](https://img.shields.io/badge/❤️-Sponsor-ff69b4?style=for-the-badge&logo=github)](https://github.com/sponsors/NguyenMinhDuc163)

# Health-care-microservice
