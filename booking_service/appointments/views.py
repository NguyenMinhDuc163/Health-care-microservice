from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Appointment
from .serializers import AppointmentSerializer

# Create your views here.

def format_response(data=None, code=200, status_str="success", message="", error=""):
    # Đảm bảo data luôn là list
    if data is None:
        data = []
    elif not isinstance(data, list):
        data = [data]
    return {
        "code": code,
        "data": data,
        "status": status_str,
        "message": message,
        "error": error
    }

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(format_response(data=serializer.data, message="Lấy danh sách lịch hẹn thành công."))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(format_response(data=serializer.data, message="Lấy chi tiết lịch hẹn thành công."))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(format_response(data=serializer.data, code=201, message="Đặt lịch thành công."), status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(format_response(data=serializer.data, message="Cập nhật lịch hẹn thành công."))

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'cancelled'
        instance.save()
        return Response(format_response(data=[], message="Hủy lịch thành công."), status=status.HTTP_204_NO_CONTENT)
