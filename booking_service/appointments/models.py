from django.db import models

# Create your models here.

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('waitlisted', 'Waitlisted'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    patient_id = models.IntegerField()
    doctor_id = models.IntegerField()
    appointment_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waitlisted')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['appointment_date']

    def __str__(self):
        return f"Appointment {self.id} - {self.patient_id} with Dr. {self.doctor_id}"
