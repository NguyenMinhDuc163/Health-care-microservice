from rest_framework import serializers
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ['id', 'patient_id', 'doctor_id', 'appointment_date', 
                 'status', 'created_at', 'updated_at', 'notes']
        read_only_fields = ['created_at', 'updated_at'] 