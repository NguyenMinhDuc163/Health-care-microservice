from django.db import models
from django.utils import timezone

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    )
    
    BLOOD_TYPE_CHOICES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )

    first_name = models.CharField(max_length=100, verbose_name="Tên")
    last_name = models.CharField(max_length=100, verbose_name="Họ")
    date_of_birth = models.DateField(verbose_name="Ngày sinh")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Giới tính")
    id_number = models.CharField(max_length=20, verbose_name="Số CMND/CCCD")
    address = models.TextField(verbose_name="Địa chỉ")
    phone_number = models.CharField(max_length=15, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True, verbose_name="Nhóm máu")
    medical_history = models.TextField(blank=True, null=True, verbose_name="Tiền sử bệnh")
    allergies = models.TextField(blank=True, null=True, verbose_name="Dị ứng")
    registration_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày đăng ký")
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Bệnh nhân"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def full_name(self):
        return f"{self.last_name} {self.first_name}"

class MedicalRecord(models.Model):
    TREATMENT_STATUS_CHOICES = (
        ('PENDING', 'Chờ điều trị'),
        ('IN_PROGRESS', 'Đang điều trị'),
        ('COMPLETED', 'Đã hoàn thành'),
        ('CANCELLED', 'Đã hủy'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records', verbose_name="Bệnh nhân")
    examination_date = models.DateTimeField(default=timezone.now, verbose_name="Ngày khám")
    diagnosis = models.TextField(verbose_name="Chẩn đoán")
    prescription = models.TextField(verbose_name="Đơn thuốc")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    doctor = models.CharField(max_length=100, verbose_name="Bác sĩ điều trị")
    department = models.CharField(max_length=100, verbose_name="Khoa phòng")
    treatment_status = models.CharField(max_length=20, choices=TREATMENT_STATUS_CHOICES, default='PENDING', verbose_name="Trạng thái điều trị")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Hồ sơ bệnh án"
        verbose_name_plural = "Hồ sơ bệnh án"
        ordering = ['-examination_date']

    def __str__(self):
        return f"Hồ sơ bệnh án của {self.patient.full_name()} - {self.examination_date.strftime('%d/%m/%Y')}" 