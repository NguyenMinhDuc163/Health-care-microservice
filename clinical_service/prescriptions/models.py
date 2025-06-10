from django.db import models

# Create your models here.

class Prescription(models.Model):
    medical_record_id = models.IntegerField()
    patient_id = models.IntegerField(null=True, blank=True)
    medicine_id = models.IntegerField()
    medicine_name = models.CharField(max_length=255)
    medicine_description = models.TextField()
    medicine_price = models.DecimalField(max_digits=10, decimal_places=2)
    medicine_manufacturer = models.CharField(max_length=255)
    medicine_expiry_date = models.DateField()
    quantity = models.IntegerField()
    dosage = models.CharField(max_length=255)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prescriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Đơn thuốc {self.id} - {self.medicine_name}"
