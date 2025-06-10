#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gateway.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Thêm cấu hình cho pharmacy service
    os.environ.setdefault('PHARMACY_SERVICE_URL', 'http://pharmacy-service:8004')
    # Thêm cấu hình cho clinical service
    os.environ.setdefault('CLINICAL_SERVICE_URL', 'http://clinical-service:8005')
    # Thêm cấu hình cho payment service
    os.environ.setdefault('PAYMENT_SERVICE_URL', 'http://payment-service:8006')
    
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
