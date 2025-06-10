from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.db import models
from .models import Patient, MedicalRecord
from .serializers import PatientSerializer, MedicalRecordSerializer
from .utils import CustomResponse

class PatientFilter(filters.FilterSet):
    name = filters.CharFilter(method='filter_by_name')
    date_of_birth = filters.DateFilter()
    gender = filters.CharFilter()
    id_number = filters.CharFilter()

    class Meta:
        model = Patient
        fields = ['name', 'date_of_birth', 'gender', 'id_number']

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(
            models.Q(first_name__icontains=value) |
            models.Q(last_name__icontains=value)
        )

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.filter(is_active=True)
    serializer_class = PatientSerializer
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name', 'id_number', 'phone_number']
    ordering_fields = ['created_at', 'registration_date', 'first_name', 'last_name']
    ordering = ['-created_at']

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(serializer.data, "Lấy danh sách bệnh nhân thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi lấy danh sách bệnh nhân", error=e)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.success(serializer.data, "Lấy thông tin bệnh nhân thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi lấy thông tin bệnh nhân", error=e)

    def create(self, request, *args, **kwargs):
        try:
            patient_id = self.kwargs.get('patient_pk')
            # Kiểm tra xem bệnh nhân có tồn tại không
            if not Patient.objects.filter(id=patient_id, is_active=True).exists():
                return CustomResponse.error(f"Không tìm thấy bệnh nhân với ID {patient_id}")
                
            data = request.data.copy()
            data['patient'] = patient_id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return CustomResponse.success(serializer.data, "Tạo hồ sơ bệnh án thành công", code=201)
        except Exception as e:
            return CustomResponse.error("Lỗi khi tạo hồ sơ bệnh án", error=e)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return CustomResponse.success(serializer.data, "Cập nhật bệnh nhân thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi cập nhật bệnh nhân", error=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return CustomResponse.success(message="Xóa bệnh nhân thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi xóa bệnh nhân", error=e)

class MedicalRecordFilter(filters.FilterSet):
    examination_date = filters.DateFilter()
    treatment_status = filters.CharFilter()
    doctor = filters.CharFilter(lookup_expr='icontains')
    department = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = MedicalRecord
        fields = ['examination_date', 'treatment_status', 'doctor', 'department']

class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    filterset_class = MedicalRecordFilter
    search_fields = ['diagnosis', 'prescription', 'notes', 'doctor', 'department']
    ordering_fields = ['examination_date', 'created_at', 'treatment_status']
    ordering = ['-examination_date']

    def get_queryset(self):
        patient_id = self.kwargs.get('patient_pk')
        return MedicalRecord.objects.filter(patient_id=patient_id)

    def perform_create(self, serializer):
        patient_id = self.kwargs.get('patient_pk')
        serializer.save(patient_id=patient_id)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.get_serializer(queryset, many=True)
            return CustomResponse.success(serializer.data, "Lấy danh sách hồ sơ bệnh án thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi lấy danh sách hồ sơ bệnh án", error=e)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return CustomResponse.success(serializer.data, "Lấy thông tin hồ sơ bệnh án thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi lấy thông tin hồ sơ bệnh án", error=e)

    def create(self, request, *args, **kwargs):
        try:
            patient_id = self.kwargs.get('patient_pk')
            # Kiểm tra xem bệnh nhân có tồn tại không
            if not Patient.objects.filter(id=patient_id, is_active=True).exists():
                return CustomResponse.error(f"Không tìm thấy bệnh nhân với ID {patient_id}")
                
            data = request.data.copy()
            data['patient'] = patient_id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return CustomResponse.success(serializer.data, "Tạo hồ sơ bệnh án thành công", code=201)
        except Exception as e:
            return CustomResponse.error("Lỗi khi tạo hồ sơ bệnh án", error=e)

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            data = request.data.copy()
            data['patient'] = self.kwargs.get('patient_pk')
            serializer = self.get_serializer(instance, data=data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return CustomResponse.success(serializer.data, "Cập nhật hồ sơ bệnh án thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi cập nhật hồ sơ bệnh án", error=e)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return CustomResponse.success(message="Xóa hồ sơ bệnh án thành công")
        except Exception as e:
            return CustomResponse.error("Lỗi khi xóa hồ sơ bệnh án", error=e) 