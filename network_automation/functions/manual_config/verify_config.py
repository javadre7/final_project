from django.shortcuts import render, get_object_or_404, redirect
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime

def verify_configure(request):
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        mikrotik_command = request.POST['mikrotik_command'].splitlines()
        cisco_command = request.POST['cisco_command'].splitlines()
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                if dev.vendor.lower() == 'mikrotik':
                    for cmd in mikrotik_command:
                        stdin, stdout, stderr = ssh_client.exec_command(cmd)
                        result.append(f'[[[Result on {dev.ip_address}]]]')
                        result.append(stdout.read().decode())
                else:
                    conn = ssh_client.invoke_shell()
                    conn.send('terminal length 0\n')
                    for cmd in cisco_command:
                        result.append(f"[[[Result on {dev.ip_address}]]]")
                        conn.send(cmd + "\n")
                        time.sleep(2)
                        output = conn.recv(65535)
                        result.append(output.decode())
                log = Log(target=dev.ip_address, action='Verify Config', status='Success', time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action='Verify Config', status='Error', time=datetime.now(), messages=e)
                log.save()

        result = '\n'.join(result)
        context = {
            'result' : result,
            'mode' : 'Verify Config'
        }
        return render(request, 'result.html', context)

    else:
        devices = Device.objects.all()
        context = {
            'devices': devices,
            'mode': 'Verify Config',
        }
        return render(request, 'config.html', context)