from django.shortcuts import render
from network_automation.models import Log

def log(request):
    logs = Log.objects.all()

    context = {
        "logs": logs
    }

    return render(request, 'log.html', context)