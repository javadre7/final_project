from django.shortcuts import render
from network_automation.models import Device, Log

def delete_devices(request):

    Device.objects.all().delete()

    return render(request, 'reset/delete_devices.html')

def delete_logs(request):

    Log.objects.all().delete()

    return render(request, 'reset/delete_logs.html')