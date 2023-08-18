from django.shortcuts import render, get_object_or_404, redirect
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime

def configure(request):
    if request.method == 'POST':
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                if dev.vendor.lower() == 'cisco':
                    conn = ssh_client.invoke_shell()
                    conn.send("configure terminal\n")
                    for cmd in cisco_command:
                        conn.send(cmd + "\n")
                        time.sleep(2)
                else:
                    for cmd in mikrotik_command:
                        ssh_client.exec_command(cmd)
                log = Log(target=dev.ip_address, action='Configure', status='Success', time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action='Configure', status='Error', time=datetime.now(), messages=e)
                log.save()
        return redirect('home')
    
    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Configure',
        }
        return render(request, 'config.html', context)