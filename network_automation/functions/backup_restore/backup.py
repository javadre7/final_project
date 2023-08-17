from django.shortcuts import render
import subprocess, json

def backup_devices(request):
    models_to_backup = ['network_automation.Device']

    output_file = 'backup_devices.json'

    subprocess.run(['python', 'manage.py', 'dumpdata'] + models_to_backup + ['--output', output_file])
    
    file = open("backup_devices.json", 'r')
    x = file.read()
    context = {
        'json':json.loads(x),
        'mode':'devices'
    }
    return render(request, 'backup_restore/backup.html', context)

def backup_logs(request):
    models_to_backup = ['network_automation.Log']

    output_file = 'backup_logs.json'

    subprocess.run(['python', 'manage.py', 'dumpdata'] + models_to_backup + ['--output', output_file])
    
    file = open("backup_logs.json", 'r')
    x = file.read()
    context = {
        'json':json.loads(x),
        'mode':'logs'
    }
    return render(request, 'backup_restore/backup.html', context)