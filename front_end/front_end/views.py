def medical_records(request):
    return render(request, 'medical_records.html')

def doctor_schedule(request):
    return render(request, 'doctor-schedule.html')

def api_proxy(request, path):
    # ... existing code ... 