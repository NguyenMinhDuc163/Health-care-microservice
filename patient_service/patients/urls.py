from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import PatientViewSet, MedicalRecordViewSet

# Tạo router chính
router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')

# Tạo nested router cho medical records
patients_router = routers.NestedDefaultRouter(router, r'patients', lookup='patient')
patients_router.register(r'medical-records', MedicalRecordViewSet, basename='patient-medical-records')

# Kết hợp tất cả các URLs
urlpatterns = [
    path('', include(router.urls)),
    path('', include(patients_router.urls)),
    path('api-auth/', include('rest_framework.urls')),
] 