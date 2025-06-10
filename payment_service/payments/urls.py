from django.urls import path
from .views import PaymentDetailView, PaymentApproveView, PaymentListView

urlpatterns = [
    path('patients/<int:patient_id>/medical-records/<int:medical_record_id>/payment/', 
         PaymentDetailView.as_view(), 
         name='payment-detail'),
    path('payments/approve/', PaymentApproveView.as_view(), name='payment-approve'),
    path('payments/', PaymentListView.as_view(), name='payment-list'),
] 