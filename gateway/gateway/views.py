import requests
import logging
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from requests.exceptions import RequestException
from rest_framework.views import APIView
from rest_framework import status

# Cấu hình logging
logger = logging.getLogger(__name__)

AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL
PATIENT_SERVICE_URL = settings.PATIENT_SERVICE_URL
CHATBOT_SERVICE_URL = settings.CHATBOT_SERVICE_URL
BOOKING_SERVICE_URL = settings.BOOKING_SERVICE_URL
PHARMACY_SERVICE_URL = settings.PHARMACY_SERVICE_URL
CLINICAL_SERVICE_URL = settings.CLINICAL_SERVICE_URL
PAYMENT_SERVICE_URL = settings.PAYMENT_SERVICE_URL

def handle_service_response(response):
    try:
        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        logger.info(f"Response content: {response.text}")
        
        if response.status_code >= 400:
            logger.error(f"Error response from service: {response.text}")
            return Response(
                {"error": f"Service error: {response.text}"},
                status=response.status_code
            )
            
        # Nếu response rỗng và status code là 204 (No Content)
        if response.status_code == 204:
            return Response(status=204)
            
        # Nếu response rỗng nhưng không phải 204
        if not response.text:
            return Response({"message": "Success"}, status=response.status_code)
            
        try:
            return Response(response.json(), status=response.status_code)
        except ValueError as e:
            logger.error(f"Error parsing JSON response: {str(e)}")
            logger.error(f"Response content: {response.text}")
            return Response(
                {"message": response.text} if response.text else {"message": "Success"},
                status=response.status_code
            )
            
    except Exception as e:
        logger.error(f"Error handling service response: {str(e)}")
        return Response(
            {"error": f"Error processing service response: {str(e)}"},
            status=500
        )

@api_view(['POST'])
def register(request):
    try:
        logger.info(f"Forwarding register request to auth service: {request.data}")
        logger.info(f"Auth service URL: {AUTH_SERVICE_URL}/api/users/")
        
        response = requests.post(
            f'{AUTH_SERVICE_URL}/api/users/',
            json=request.data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

@api_view(['POST'])
def login(request):
    try:
        logger.info(f"Forwarding login request to auth service: {request.data}")
        response = requests.post(
            f'{AUTH_SERVICE_URL}/api/users/login/',
            json=request.data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

@api_view(['GET'])
def get_user_info(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(
            f'{AUTH_SERVICE_URL}/api/users/me/',
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

@api_view(['POST'])
def logout(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(
            f'{AUTH_SERVICE_URL}/api/users/logout/',
            json=request.data,
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

@api_view(['POST'])
def refresh_token(request):
    try:
        response = requests.post(
            f'{AUTH_SERVICE_URL}/api/token/refresh/',
            json=request.data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

@api_view(['GET'])
def get_users_by_role(request):
    """Forward request to auth service to get users by role"""
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.get(
            f'{AUTH_SERVICE_URL}/api/users/get_users_by_role/',
            headers=headers,
            params=request.GET,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to auth service: {str(e)}")
        return Response(
            {"error": f"Could not connect to auth service: {str(e)}"},
            status=503
        )

class UserView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Forwarding register request to auth service: {request.data}")
            response = requests.post(
                f"{settings.AUTH_SERVICE_URL}/api/users/",
                json=request.data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            logger.error(f"Error in UserView: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Forwarding login request to auth service: {request.data}")
            response = requests.post(
                f"{settings.AUTH_SERVICE_URL}/api/users/login/",
                json=request.data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            logger.error(f"Error in LoginView: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Patient Service Endpoints
@api_view(['GET', 'POST'])
def get_patients(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PATIENT_SERVICE_URL}/api/patients/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PATIENT_SERVICE_URL}/api/patients/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

@api_view(['POST'])
def create_patient(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(
            f'{PATIENT_SERVICE_URL}/api/patients/',
            json=request.data,
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

@api_view(['GET'])
def get_patient_detail(request, patient_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(
            f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/',
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

@api_view(['PUT'])
def update_patient(request, patient_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.put(
            f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/',
            json=request.data,
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

@api_view(['DELETE'])
def delete_patient(request, patient_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.delete(
            f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/',
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

# Medical Records Endpoints
@api_view(['GET', 'POST'])
def get_medical_records(request, patient_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'DELETE'])
def get_medical_record_detail(request, patient_id, record_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/{record_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/{record_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{PATIENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/{record_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to patient service: {str(e)}")
        return Response(
            {"error": f"Could not connect to patient service: {str(e)}"},
            status=503
        )

# Chatbot Endpoints
@api_view(['POST'])
def chat_with_bot(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(
            f'{CHATBOT_SERVICE_URL}/chat',
            json=request.data,
            headers=headers,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to chatbot service: {str(e)}")
        return Response(
            {"error": f"Could not connect to chatbot service: {str(e)}"},
            status=503
        )

# Booking Service Endpoints
@api_view(['GET', 'POST'])
def get_bookings(request):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{BOOKING_SERVICE_URL}/api/bookings/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{BOOKING_SERVICE_URL}/api/bookings/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to booking service: {str(e)}")
        return Response(
            {"error": f"Could not connect to booking service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_booking_detail(request, booking_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{BOOKING_SERVICE_URL}/api/bookings/{booking_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{BOOKING_SERVICE_URL}/api/bookings/{booking_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                f'{BOOKING_SERVICE_URL}/api/bookings/{booking_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{BOOKING_SERVICE_URL}/api/bookings/{booking_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to booking service: {str(e)}")
        return Response(
            {"error": f"Could not connect to booking service: {str(e)}"},
            status=503
        )

@api_view(['GET'])
def get_patient_bookings(request, patient_id):
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.get(
            f'{BOOKING_SERVICE_URL}/api/patients/{patient_id}/bookings/',
            headers=headers,
            params=request.GET,
            timeout=5
        )
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to booking service: {str(e)}")
        return Response(
            {"error": f"Could not connect to booking service: {str(e)}"},
            status=503
        )

# Pharmacy Service Views
@api_view(['GET', 'POST'])
def get_medicines(request):
    """Forward request to pharmacy service for medicines list"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PHARMACY_SERVICE_URL}/api/medicines/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PHARMACY_SERVICE_URL}/api/medicines/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to pharmacy service: {str(e)}")
        return Response(
            {"error": f"Could not connect to pharmacy service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_medicine_detail(request, medicine_id):
    """Forward request to pharmacy service for medicine detail"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PHARMACY_SERVICE_URL}/api/medicines/{medicine_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{PHARMACY_SERVICE_URL}/api/medicines/{medicine_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                f'{PHARMACY_SERVICE_URL}/api/medicines/{medicine_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{PHARMACY_SERVICE_URL}/api/medicines/{medicine_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to pharmacy service: {str(e)}")
        return Response(
            {"error": f"Could not connect to pharmacy service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'POST'])
def get_prescriptions(request):
    """Forward request to pharmacy service for prescriptions list"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to pharmacy service: {str(e)}")
        return Response(
            {"error": f"Could not connect to pharmacy service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_prescription_detail(request, prescription_id):
    """Forward request to pharmacy service for prescription detail"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{PHARMACY_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to pharmacy service: {str(e)}")
        return Response(
            {"error": f"Could not connect to pharmacy service: {str(e)}"},
            status=503
        )

# Clinical Service Views
@api_view(['GET', 'POST'])
def get_prescriptions(request):
    """Forward request to clinical service for prescriptions list"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to clinical service: {str(e)}")
        return Response(
            {"error": f"Could not connect to clinical service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_prescription_detail(request, prescription_id):
    """Forward request to clinical service for prescription detail"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{CLINICAL_SERVICE_URL}/api/prescriptions/{prescription_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to clinical service: {str(e)}")
        return Response(
            {"error": f"Could not connect to clinical service: {str(e)}"},
            status=503
        )

# Payment Service Views
@api_view(['GET', 'POST'])
def get_payments(request):
    """Forward request to payment service for payments list"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PAYMENT_SERVICE_URL}/api/payments/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PAYMENT_SERVICE_URL}/api/payments/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to payment service: {str(e)}")
        return Response(
            {"error": f"Could not connect to payment service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_payment_detail(request, payment_id):
    """Forward request to payment service for payment detail"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PAYMENT_SERVICE_URL}/api/payments/{payment_id}/',
                headers=headers,
                timeout=5
            )
        elif request.method == 'PUT':
            response = requests.put(
                f'{PAYMENT_SERVICE_URL}/api/payments/{payment_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        elif request.method == 'PATCH':
            response = requests.patch(
                f'{PAYMENT_SERVICE_URL}/api/payments/{payment_id}/',
                json=request.data,
                headers=headers,
                timeout=5
            )
        else:  # DELETE
            response = requests.delete(
                f'{PAYMENT_SERVICE_URL}/api/payments/{payment_id}/',
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to payment service: {str(e)}")
        return Response(
            {"error": f"Could not connect to payment service: {str(e)}"},
            status=503
        )

@api_view(['GET', 'POST'])
def get_medical_record_payment(request, patient_id, record_id):
    """Forward request to payment service for medical record payment"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if request.method == 'GET':
            response = requests.get(
                f'{PAYMENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/{record_id}/payment/',
                headers=headers,
                params=request.GET,
                timeout=5
            )
        else:  # POST
            response = requests.post(
                f'{PAYMENT_SERVICE_URL}/api/patients/{patient_id}/medical-records/{record_id}/payment/',
                json=request.data,
                headers=headers,
                timeout=5
            )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to payment service: {str(e)}")
        return Response(
            {"error": f"Could not connect to payment service: {str(e)}"},
            status=503
        )

@api_view(['POST'])
def approve_payment(request):
    """Forward request to payment service for payment approval"""
    try:
        headers = {
            'Authorization': request.headers.get('Authorization'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f'{PAYMENT_SERVICE_URL}/api/payments/approve/',
            json=request.data,
            headers=headers,
            timeout=5
        )
            
        return handle_service_response(response)
    except RequestException as e:
        logger.error(f"Error connecting to payment service: {str(e)}")
        return Response(
            {"error": f"Could not connect to payment service: {str(e)}"},
            status=503
        ) 