from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .models import Prescription
from .serializers import PrescriptionSerializer
import requests
from django.conf import settings
import time
from requests.exceptions import RequestException

# Create your views here.

class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def _format_response(self, code, status, message, data=None, error=None):
        """Format response theo chuẩn chung"""
        response = {
            "code": code,
            "status": status,
            "message": message,
            "data": data if data is not None else [],
            "error": error if error is not None else ""
        }
        return response

    def handle_exception(self, exc):
        """Xử lý tất cả các exception và trả về format chuẩn"""
        if isinstance(exc, NotFound):
            return Response(
                self._format_response(
                    code=404,
                    status="error",
                    message="Không tìm thấy đơn thuốc",
                    error=str(exc)
                ),
                status=status.HTTP_404_NOT_FOUND
            )
        elif isinstance(exc, ValidationError):
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="Dữ liệu không hợp lệ",
                    error=str(exc)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(
                self._format_response(
                    code=200,
                    status="success",
                    message="Lấy thông tin đơn thuốc thành công",
                    data=[serializer.data]
                )
            )
        except Prescription.DoesNotExist:
            return Response(
                self._format_response(
                    code=404,
                    status="error",
                    message="Không tìm thấy đơn thuốc",
                    error=f"Không tìm thấy đơn thuốc với id {kwargs.get('pk')}"
                ),
                status=status.HTTP_404_NOT_FOUND
            )

    def list(self, request, *args, **kwargs):
        patient_id = request.query_params.get('patient_id')
        
        if patient_id:
            try:
                # Lấy tất cả đơn thuốc của bệnh nhân
                prescriptions = Prescription.objects.filter(patient_id=patient_id)
                if not prescriptions.exists():
                    return Response(
                        self._format_response(
                            code=404,
                            status="error",
                            message="Không tìm thấy đơn thuốc nào cho bệnh nhân này",
                            error=f"Không tìm thấy đơn thuốc cho patient_id {patient_id}"
                        ),
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = self.get_serializer(prescriptions, many=True)
                return Response(
                    self._format_response(
                        code=200,
                        status="success",
                        message="Lấy danh sách đơn thuốc thành công",
                        data=serializer.data
                    )
                )
            except Exception as e:
                return Response(
                    self._format_response(
                        code=400,
                        status="error",
                        message="Lỗi khi lấy danh sách đơn thuốc",
                        error=str(e)
                    ),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Nếu không có patient_id, trả về tất cả đơn thuốc
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            self._format_response(
                code=200,
                status="success",
                message="Lấy danh sách đơn thuốc thành công",
                data=serializer.data
            )
        )

    def _make_request_with_retry(self, url, method='get', **kwargs):
        """Thực hiện request với cơ chế retry"""
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if method.lower() == 'get':
                    response = requests.get(url, **kwargs)
                elif method.lower() == 'post':
                    response = requests.post(url, **kwargs)
                elif method.lower() == 'put':
                    response = requests.put(url, **kwargs)
                elif method.lower() == 'delete':
                    response = requests.delete(url, **kwargs)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response
            except RequestException as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise e
                time.sleep(retry_delay)
                continue

    def create(self, request, *args, **kwargs):
        medicine_id = request.data.get('medicine_id')
        medical_record_id = request.data.get('medical_record_id')
        patient_id = request.data.get('patient_id')
        
        # Validate required fields
        if not medicine_id:
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="medicine_id là bắt buộc",
                    error="medicine_id is required"
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not medical_record_id:
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="medical_record_id là bắt buộc",
                    error="medical_record_id is required"
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if not patient_id:
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="patient_id là bắt buộc",
                    error="patient_id is required"
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lấy thông tin thuốc từ API
        try:
            medicine_response = self._make_request_with_retry(
                f'{settings.GATEWAY_URL}/api/medicines/{medicine_id}/',
                headers={'Accept': 'application/json'}
            )
            medicine_data = medicine_response.json()
        except RequestException as e:
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="Không thể lấy thông tin thuốc",
                    error=str(e)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Lấy thông tin bệnh án từ API
        try:
            medical_record_response = self._make_request_with_retry(
                f'{settings.GATEWAY_URL}/api/patients/{patient_id}/medical-records/{medical_record_id}/',
                headers={'Accept': 'application/json'}
            )
            medical_record_data = medical_record_response.json()
        except RequestException as e:
            return Response(
                self._format_response(
                    code=400,
                    status="error",
                    message="Không thể lấy thông tin bệnh án",
                    error=str(e)
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Tạo đơn thuốc mới
        prescription_data = {
            'medical_record_id': medical_record_id,
            'patient_id': patient_id,
            'medicine_id': medicine_id,
            'medicine_name': medicine_data['name'],
            'medicine_description': medicine_data['description'],
            'medicine_price': medicine_data['price'],
            'medicine_manufacturer': medicine_data['manufacturer'],
            'medicine_expiry_date': medicine_data['expiry_date'],
            'quantity': request.data.get('quantity'),
            'dosage': request.data.get('dosage'),
            'notes': request.data.get('notes')
        }
        
        serializer = self.get_serializer(data=prescription_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            self._format_response(
                code=201,
                status="success",
                message="Tạo đơn thuốc thành công",
                data=[serializer.data]
            ),
            status=status.HTTP_201_CREATED
        )
