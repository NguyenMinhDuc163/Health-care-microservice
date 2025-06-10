"""
URL configuration for front_end project.

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
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect

def redirect_to_gateway(request, path):
    return HttpResponseRedirect(f'http://localhost:8080/{path}')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='login.html'), name='login'),
    path('login/', TemplateView.as_view(template_name='login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='register.html'), name='register'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('patients/', TemplateView.as_view(template_name='patients.html'), name='patients'),
    path('prescription/<int:patient_id>/', TemplateView.as_view(template_name='prescription.html'), name='prescription'),
    path('prescription/<int:patient_id>/payment/', TemplateView.as_view(template_name='payment.html'), name='payment'),
    path('medical-records/', TemplateView.as_view(template_name='medical_records.html'), name='medical_records'),
    path('doctor-schedule/', TemplateView.as_view(template_name='doctor-schedule.html'), name='doctor_schedule'),
    path('pharmacy/', TemplateView.as_view(template_name='pharmacy.html'), name='pharmacy'),
    path('prescriptions/', TemplateView.as_view(template_name='prescriptions.html'), name='prescriptions'),
    path('api/<path:path>', redirect_to_gateway, name='api'),
]
