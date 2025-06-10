from rest_framework import serializers
from .models import Payment

class PaymentDetailSerializer(serializers.Serializer):
    patient_name = serializers.CharField()
    diagnosis = serializers.CharField()
    doctor = serializers.CharField()
    payment_status = serializers.CharField()
    medicines = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_status']

class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__' 