# Hướng Dẫn Đóng Góp

Cảm ơn bạn quan tâm đến dự án Healthcare Microservice! 🏥

## 🚀 Cách Đóng Góp

### 🐛 Báo Cáo Lỗi
- Tìm kiếm trong [Issues](../../issues) trước
- Mô tả rõ ràng lỗi và cách tái tạo
- Kèm screenshots nếu có

### ✨ Đề Xuất Tính Năng
- Giải thích rõ use case
- Thảo luận trong [Discussions](../../discussions) trước

### 💻 Đóng Góp Code
1. Fork repository
2. Tạo branch: `git checkout -b feature/ten-tinh-nang`
3. Commit: `git commit -m "feat: add new feature"`
4. Push: `git push origin feature/ten-tinh-nang`
5. Tạo Pull Request

## 📏 Quy Tắc Code

### Python
```python
# Sử dụng Black formatter
black .

# Type hints bắt buộc
def create_patient(data: dict) -> Patient:
    """Create new patient."""
    pass
```

### Commit Messages
```bash
feat(auth): add JWT authentication
fix(patient): resolve validation bug
docs: update API documentation
```

## 🧪 Testing
```bash
# Chạy tests
python -m pytest

# Với Docker
docker-compose up --build
```

## 🔒 Bảo Mật Y Tế

**⚠️ QUAN TRỌNG:**
- **KHÔNG** sử dụng dữ liệu bệnh nhân thật
- **LUÔN** dùng dummy data để test
- **TUÂN THỦ** HIPAA compliance
- Báo cáo security issues riêng tư

## 📞 Hỗ Trợ

- **Issues**: [Tạo issue mới](../../issues/new)
- **Discussions**: [Q&A và thảo luận](../../discussions)
- **Maintainer**: [@NguyenMinhDuc163](https://github.com/NguyenMinhDuc163)

## 🤝 Cộng Đồng

Tham gia cộng đồng healthcare open source:
- ⭐ Star repository nếu hữu ích
- 🍴 Fork và đóng góp code
- 📢 Chia sẻ với đồng nghiệp
- 💬 Thảo luận và góp ý

## 📋 Checklist Trước Khi Submit

- [ ] Code đã được test
- [ ] Tuân thủ coding standards
- [ ] Documentation đã cập nhật
- [ ] Không có dữ liệu nhạy cảm
- [ ] Security requirements được đáp ứng

---

**Cảm ơn bạn đã đóng góp vào việc cải thiện công nghệ y tế! 🏥** 