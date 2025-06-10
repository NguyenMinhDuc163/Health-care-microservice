from rest_framework import serializers
from .models import Patient, MedicalRecord
from django.utils import timezone

class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'date_of_birth',
            'gender', 'id_number', 'address', 'phone_number', 'email',
            'blood_type', 'medical_history', 'allergies', 'registration_date',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'registration_date', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.full_name()

class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    patient = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'patient', 'patient_name', 'examination_date', 'diagnosis',
            'prescription', 'notes', 'doctor', 'department', 'treatment_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.full_name()

    def validate_examination_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Ngày khám không thể là ngày trong tương lai")
        return value

    def validate(self, data):
        if 'patient' in data and not data['patient'].is_active:
            raise serializers.ValidationError({"patient": "Bệnh nhân này đã bị xóa hoặc không còn hoạt động"})
        return data 