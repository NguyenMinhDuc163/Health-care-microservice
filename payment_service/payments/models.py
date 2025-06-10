from django.db import models

# Create your models here.

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('PENDING', 'Chờ thanh toán'),
        ('COMPLETED', 'Đã thanh toán'),
        ('FAILED', 'Thanh toán thất bại'),
    )

    patient_id = models.IntegerField()
    medical_record_id = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    payment_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
