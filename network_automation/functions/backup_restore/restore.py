from django.shortcuts import render
import subprocess, json

def restore_devices(request):
    try:
        input_file = 'backup_devices.json'
        
        subprocess.run(['python', 'manage.py', 'loaddata', input_file])
        
        file = open("backup_devices.json", 'r')
        x = file.read()
        context = {
            'json':json.loads(x)
        }
        return render(request, 'backup_restore/restore.html', context)
    except Exception as e:
        context = {
            'error_text' : 'error',
        }
        return render(request, 'backup_restore/restore_error.html')

def restore_logs(request):
    try:
        input_file = 'backup_logs.json'
        
        subprocess.run(['python', 'manage.py', 'loaddata', input_file])
        
        file = open("backup_logs.json", 'r')
        x = file.read()
        context = {
            'json':json.loads(x)
        }
        return render(request, 'backup_restore/restore.html', context)
    except Exception as e:
        context = {
            'error_text' : 'error',
        }
        return render(request, 'backup_restore/restore_error.html')
