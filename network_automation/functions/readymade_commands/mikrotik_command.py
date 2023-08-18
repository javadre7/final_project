from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log
import paramiko
from datetime import datetime

def mikrotik_command(request, cmd):
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                stdin, stdout, stderr = ssh_client.exec_command(cmd)

                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(stdout.read().decode())
                
                log = Log(target=dev.ip_address, action=f'cmd({cmd})', status='Success', time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action=f'cmd({cmd})', status='Error', time=datetime.now(), messages=e)
                log.save()
    
        result = '\n'.join(result)
        return render(request, 'result.html', {'result':result})

    else:
        devices = Device.objects.filter(vendor='mikrotik')
        context = {
            'devices': devices,
            'mode' : f'Sending "{cmd}" command to MikroTik Device',
            'model' : 'MikroTik',
        }
        
        return render(request, 'command.html', context)