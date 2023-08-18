from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime

def ssh_telnet(request):
    if request.method == 'POST':
        additional_attr = request.POST.get('additional')
        if additional_attr == 'one':
            try:
                request.session['device'] = selected_device_id = request.POST.getlist('device')[0]
                dev = get_object_or_404(Device, pk = selected_device_id)
                device_model = dev.vendor.lower()

                if (device_model == 'cisco'):
                    return render(request, 'ssh_telnet/ssh_telnet_cisco.html')
                else:
                    return render(request, 'ssh_telnet/ssh_telnet_mikrotik.html')
            except Exception as e:
                return ssh_telnet_except(request, e, dev, True)
        elif additional_attr == 'two':
            try:
                var = request.session.get('device')
                ssh_sw = request.POST.get('ssh')
                telnet_sw = request.POST.get('telnet')

                if(request.POST.get('ssh')=='on'):
                    ssh = 'ssh'
                else:
                    ssh = ''
                if(request.POST.get('telnet')=='on'):
                    telnet = 'telnet'
                else:
                    telnet = ''
                connections = request.POST.get('connections')

                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                conn = ssh_client.invoke_shell()
                conn.send('terminal length 0\n')
                conn.send('configure terminal\n')
                conn.send(f'line vty 0 {int(connections)-1}\n')
                if(ssh == '' and telnet == ''):
                    conn.send(f'transport input none\n')
                else:
                    conn.send(f'transport input {ssh} {telnet}\n')
                log = Log(target=dev.ip_address, action=f'cmd(ssh:{"off" if request.POST.get("ssh")==None else "on"},telnet:{"off" if request.POST.get("telnet")==None else "on"})', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                time.sleep(2)
                output = conn.recv(65535)
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(output.decode())
                result = '\n'.join(result)

                return render(request, 'result.html', {'result' : result})
            except Exception as e:
                return ssh_telnet_except(request, e, dev, False, "off" if request.POST.get("ssh")==None else "on", "off" if request.POST.get("telnet")==None else "on")
        elif additional_attr == 'three':
            try:
                var = request.session.get('device')
                ssh_sw = request.POST.get('ssh')
                telnet_sw = request.POST.get('telnet')

                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                if(request.POST.get('telnet')=='on'):
                    stdin, stdout, stderr = ssh_client.exec_command("ip service enable telnet")
                else:
                    stdin, stdout, stderr = ssh_client.exec_command("ip service disable telnet")
                if(request.POST.get('ssh')=='on'):
                    stdin, stdout, stderr = ssh_client.exec_command("ip service enable ssh")
                else:
                    stdin, stdout, stderr = ssh_client.exec_command("ip service disable ssh")
                log = Log(target=dev.ip_address, action=f'cmd(ssh:{"off" if request.POST.get("ssh")==None else "on"},telnet:{"off" if request.POST.get("telnet")==None else "on"})', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(stdout.read().decode())
                result = '\n'.join(result)

                context = {
                    'result' : result,
                    'ssh_telnet' : f'configurations applied successfully: ssh:{"off" if request.POST.get("ssh")==None else "on"}, telnet:{"off" if request.POST.get("telnet")==None else "on"}'
                }
                return render(request, 'result.html', context)
            except Exception as e:
                return ssh_telnet_except(request, e, dev, False, "off" if request.POST.get("ssh")==None else "on", "off" if request.POST.get("telnet")==None else "on")
    else:
        devices = Device.objects.all()
        context = {
            'devices' : devices,
        }
        return render(request, 'ssh_telnet/ssh_telnet.html', context)

def ssh_telnet_except(request, e, dev, first_form, ssh_sw=None, telnet_sw=None):
    if (first_form == False):
        log = Log(target=dev.ip_address, action=f'cmd(ssh:{ssh_sw},telnet:{telnet_sw})', status='Error', time=datetime.now(), messages=e)
        log.save()
    devices = Device.objects.all()
    context = {
        'devices' : devices,
        'error_text' : 'there was ssh error connection with the IP: ',
        'error_ip' : dev.ip_address,
    }
    return render(request, 'ssh_telnet/ssh_telnet.html', context)
