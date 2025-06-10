from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler

class CustomResponse:
    @staticmethod
    def success(data=None, message="Thành công", code=200):
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data]
            
        return Response({
            "code": code,
            "data": data,
            "status": "success",
            "message": message,
            "error": ""
        }, status=code)

    @staticmethod
    def error(message="Có lỗi xảy ra", code=400, error=None):
        return Response({
            "code": code,
            "data": [],
            "status": "error",
            "message": message,
            "error": str(error) if error else message
        }, status=code)

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        error_message = str(exc)
        if hasattr(exc, 'detail'):
            if isinstance(exc.detail, list):
                error_message = exc.detail[0]
            elif isinstance(exc.detail, dict):
                error_message = next(iter(exc.detail.values()))[0]
            else:
                error_message = str(exc.detail)

        return CustomResponse.error(
            message="Có lỗi xảy ra",
            code=response.status_code,
            error=error_message
        )
    
    return CustomResponse.error(
        message="Có lỗi xảy ra",
        code=500,
        error=str(exc)
    ) 