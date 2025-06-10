"""
URL configuration for gateway project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from .views import (
    UserView, LoginView, register, login, get_user_info, 
    logout, refresh_token, get_users_by_role, get_patients, create_patient,
    get_patient_detail, update_patient, delete_patient,
    get_medical_records, get_medical_record_detail, chat_with_bot,
    get_bookings, get_booking_detail, get_patient_bookings,
    get_medicines, get_medicine_detail, get_prescriptions, get_prescription_detail,
    get_payments, get_payment_detail, get_medical_record_payment,
    approve_payment
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Auth endpoints
    path('api/users/', UserView.as_view(), name='register'),
    path('api/users/login/', LoginView.as_view(), name='login'),
    path('api/users/me/', get_user_info, name='get_user_info'),
    path('api/users/logout/', logout, name='logout'),
    path('api/users/get_users_by_role/', get_users_by_role, name='get_users_by_role'),
    path('api/token/refresh/', refresh_token, name='refresh_token'),
    
    # Patient endpoints
    path('api/patients/', get_patients, name='get_patients'),  # GET: list, POST: create
    path('api/patients/<int:patient_id>/', get_patient_detail, name='get_patient_detail'),  # GET: detail, PUT: update, DELETE: delete
    
    # Medical Records endpoints
    path('api/patients/<int:patient_id>/medical-records/', get_medical_records, name='get_medical_records'),  # GET: list, POST: create
    path('api/patients/<int:patient_id>/medical-records/<int:record_id>/', get_medical_record_detail, name='get_medical_record_detail'),  # GET: detail, PUT: update, DELETE: delete
    path('api/patients/<int:patient_id>/medical-records/<int:record_id>/payment/', get_medical_record_payment, name='get_medical_record_payment'),  # GET: get payment, POST: create payment
    
    # Chatbot endpoints
    path('api/chatbot/chat/', chat_with_bot, name='chat_with_bot'),
    
    # Booking endpoints
    path('api/appointments/', get_bookings, name='get_bookings'),
    path('api/appointments/<int:booking_id>/', get_booking_detail, name='get_booking_detail'),
    path('api/patients/<int:patient_id>/appointments/', get_patient_bookings, name='get_patient_bookings'),

    # Pharmacy endpoints
    path('api/medicines/', get_medicines, name='get_medicines'),  # GET: list, POST: create
    path('api/medicines/<int:medicine_id>/', get_medicine_detail, name='get_medicine_detail'),  # GET: detail, PUT/PATCH: update, DELETE: delete
    
    # Clinical endpoints
    path('api/prescriptions/', get_prescriptions, name='get_prescriptions'),  # GET: list, POST: create
    path('api/prescriptions/<int:prescription_id>/', get_prescription_detail, name='get_prescription_detail'),  # GET: detail, PUT/PATCH: update, DELETE: delete

    # Payment endpoints
    path('api/payments/', get_payments, name='get_payments'),  # GET: list, POST: create
    path('api/payments/<int:payment_id>/', get_payment_detail, name='get_payment_detail'),  # GET: detail, PUT/PATCH: update, DELETE: delete
    path('api/payments/approve/', approve_payment, name='approve_payment'),
]
