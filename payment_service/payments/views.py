from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import logging
from .serializers import PaymentDetailSerializer, PaymentUpdateSerializer, PaymentListSerializer
from .models import Payment
from rest_framework import generics
from django.db import transaction
from django.conf import settings

# Cấu hình logging
logger = logging.getLogger(__name__)

# Create your views here.

class PaymentDetailView(APIView):
    def get(self, request, patient_id, medical_record_id):
        try:
            # Lấy thông tin đơn thuốc
            prescriptions_url = f'{settings.CLINICAL_SERVICE_URL}/api/prescriptions/?patient_id={patient_id}'
            logger.info(f"Requesting prescriptions from: {prescriptions_url}")
            prescriptions_response = requests.get(prescriptions_url)
            logger.info(f"Prescriptions response status: {prescriptions_response.status_code}")
            logger.info(f"Prescriptions response content: {prescriptions_response.text}")
            
            try:
                prescriptions_data = prescriptions_response.json()
            except ValueError as e:
                logger.error(f"Error parsing prescriptions JSON: {str(e)}")
                return Response({
                    'code': 500,
                    'data': {},
                    'status': 'error',
                    'message': 'Lỗi khi xử lý dữ liệu từ clinical service',
                    'error': f'Invalid JSON response from clinical service: {str(e)}'
                })

            # Lấy thông tin bệnh nhân
            medical_record_url = f'{settings.CLINICAL_SERVICE_URL}/api/patients/{patient_id}/medical-records/{medical_record_id}/'
            logger.info(f"Requesting medical record from: {medical_record_url}")
            medical_record_response = requests.get(medical_record_url)
            logger.info(f"Medical record response status: {medical_record_response.status_code}")
            logger.info(f"Medical record response content: {medical_record_response.text}")
            
            try:
                medical_record_data = medical_record_response.json()
            except ValueError as e:
                logger.error(f"Error parsing medical record JSON: {str(e)}")
                return Response({
                    'code': 500,
                    'data': {},
                    'status': 'error',
                    'message': 'Lỗi khi xử lý dữ liệu từ clinical service',
                    'error': f'Invalid JSON response from clinical service: {str(e)}'
                })

            if prescriptions_data.get('code') != 200 or medical_record_data.get('code') != 200:
                logger.error(f"Error from clinical service. Prescriptions: {prescriptions_data}, Medical record: {medical_record_data}")
                return Response({
                    'code': 400,
                    'data': {},
                    'status': 'error',
                    'message': 'Không thể lấy thông tin từ các service khác',
                    'error': 'Service error'
                })

            # Xử lý dữ liệu
            medicines = []
            total_amount = 0

            for prescription in prescriptions_data.get('data', []):
                medicine = {
                    'name': prescription['medicine_name'],
                    'price': prescription['medicine_price'],
                    'quantity': prescription['quantity']
                }
                medicines.append(medicine)
                total_amount += float(prescription['medicine_price']) * prescription['quantity']

            medical_record = medical_record_data.get('data', [{}])[0]
            payment_data = {
                'patient_name': medical_record.get('patient_name', ''),
                'diagnosis': medical_record.get('diagnosis', ''),
                'doctor': medical_record.get('doctor', ''),
                'payment_status': medical_record.get('treatment_status', ''),
                'medicines': medicines,
                'total_amount': total_amount
            }

            # Tìm hoặc tạo mới Payment
            with transaction.atomic():
                payment_obj, created = Payment.objects.get_or_create(
                    patient_id=patient_id,
                    medical_record_id=medical_record_id,
                    defaults={
                        'total_amount': total_amount,
                        'payment_status': 'PENDING',
                    }
                )
                # Nếu đã có, cập nhật lại total_amount nếu cần
                if not created and payment_obj.total_amount != total_amount:
                    payment_obj.total_amount = total_amount
                    payment_obj.save()

            serializer = PaymentDetailSerializer(data=payment_data)
            if serializer.is_valid():
                qr_url = request.build_absolute_uri('/static/qr.jpg').replace('payment-service', '127.0.0.1')
                data = serializer.data
                data['qr_code_url'] = qr_url
                data['payment_id'] = payment_obj.id
                return Response({
                    'code': 200,
                    'data': data,
                    'status': 'success',
                    'message': 'Lấy thông tin thanh toán thành công',
                    'error': ''
                })
            return Response({
                'code': 400,
                'data': {},
                'status': 'error',
                'message': 'Dữ liệu không hợp lệ',
                'error': serializer.errors
            })

        except requests.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return Response({
                'code': 500,
                'data': {},
                'status': 'error',
                'message': 'Lỗi kết nối đến clinical service',
                'error': str(e)
            })
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({
                'code': 500,
                'data': {},
                'status': 'error',
                'message': 'Lỗi server',
                'error': str(e)
            })

class PaymentApproveView(APIView):
    def post(self, request):
        try:
            payment_id = request.data.get('payment_id')
            payment_status = request.data.get('payment_status')
            if not payment_id or not payment_status:
                return Response({
                    'code': 400,
                    'data': {},
                    'status': 'error',
                    'message': 'Thiếu payment_id hoặc payment_status',
                    'error': 'Missing fields'
                })
            payment = Payment.objects.get(id=payment_id)
            serializer = PaymentUpdateSerializer(payment, data={'payment_status': payment_status}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'code': 200,
                    'data': serializer.data,
                    'status': 'success',
                    'message': 'Cập nhật trạng thái thanh toán thành công',
                    'error': ''
                })
            return Response({
                'code': 400,
                'data': {},
                'status': 'error',
                'message': 'Dữ liệu không hợp lệ',
                'error': serializer.errors
            })
        except Payment.DoesNotExist:
            return Response({
                'code': 404,
                'data': {},
                'status': 'error',
                'message': 'Không tìm thấy giao dịch thanh toán',
                'error': 'Not found'
            })
        except Exception as e:
            return Response({
                'code': 500,
                'data': {},
                'status': 'error',
                'message': 'Lỗi server',
                'error': str(e)
            })

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all().order_by('-id')
    serializer_class = PaymentListSerializer
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'code': 200,
            'data': response.data,
            'status': 'success',
            'message': 'Lấy danh sách giao dịch thành công',
            'error': ''
        })
