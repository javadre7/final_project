from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log

def home(request):
    all_device = Device.objects.all()
    cisco_device = Device.objects.filter(vendor='cisco')
    mikrotik_device = Device.objects.filter(vendor='mikrotik')
    last_event = Log.objects.all().order_by('-time')[:10]

    context = {
        'all_device': len(all_device),
        'cisco_device': len(cisco_device),
        'mikrotik_device': len(mikrotik_device),
        'last_event': last_event,
    }
    return render(request, 'home.html', context)

def devices(request):
    all_device = Device.objects.all()

    context = {
        'all_device': all_device,
    }

    return render(request, 'devices.html', context)
