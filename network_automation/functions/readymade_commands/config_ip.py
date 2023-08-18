from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime
import re

def config_ip(request):
    if request.method == 'POST':
        additional_attr = request.POST.get('additional')
        if additional_attr == 'one':
            try:
                request.session['device'] = selected_device_id = request.POST.getlist('device')[0]
                dev = get_object_or_404(Device, pk = selected_device_id)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                result = []
                interface_names = []
                device_model = ''
                if dev.vendor.lower() == 'cisco':
                    device_model = dev.vendor.lower()
                    conn = ssh_client.invoke_shell()
                    conn.send('terminal length 0\n')
                    conn.send("show ip interface brief" + "\n")
                    time.sleep(2)
                    output = conn.recv(65535)
                    result.append(output.decode())
    
                    lines = result[0].strip().split("\n")
                    for line in lines[3:]:
                        match = re.match(r"^(\S+)", line)
                        if match:
                            interface_names.append(match.group(1))
                    interface_names.pop()
                else:
                    device_model = dev.vendor.lower()
                    stdin, stdout, stderr = ssh_client.exec_command("interface print")
                    result.append(f'[[[Result on {dev.ip_address}]]]')
                    result.append(stdout.read().decode())
                    second_element = result[1]
                    lines = second_element.split("\r\n")
                    lines = [line.strip() for line in lines]
                    index = next((i for i, line in enumerate(lines) if line.startswith('#     NAME')), None)
                    if index is not None:
                        lines = lines[index+1:]
                    words = []
                    for line in lines:
                        segments = line.split()
                        if len(segments) >= 3:
                            words.append(segments[2])
                    interface_names = words
            
                context = {
                    'interfaces' : interface_names,
                }
                if (device_model == 'cisco'):
                    return render(request, 'config_ip/config_ip_cisco.html', context)
                else:
                    return render(request, 'config_ip/config_ip_mikrotik.html', context)
            except Exception as e:
                return ip_except(request, e, dev)
        elif additional_attr == 'two':
            try:
                var = request.session.get('device')
                interface = request.POST.get("interface")
                ip = request.POST.get("ip")
                ip2 = request.POST.get("ip2")
                ip3 = request.POST.get("ip3")
                ip4 = request.POST.get("ip4")
                mask = request.POST.get("mask")
                mask2 = request.POST.get("mask2")
                mask3 = request.POST.get("mask3")
                mask4 = request.POST.get("mask4")
                setOrDel = request.POST.get("setOrDel")
                
                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                conn = ssh_client.invoke_shell()
                conn.send('terminal length 0\n')
                conn.send("configure terminal" + "\n")
                conn.send(f"interface {interface}" + "\n")
                if(setOrDel == 'set'):
                    conn.send(f"ip address {ip}.{ip2}.{ip3}.{ip4} {mask}.{mask2}.{mask3}.{mask4}" + "\n")
                    conn.send("no shutdown" + "\n")
                    log = Log(target=dev.ip_address, action='cmd(Set IP Address)', status='Success', time=datetime.now(), messages="No Error")
                else:
                    conn.send(f"no ip address {ip}.{ip2}.{ip3}.{ip4} {mask}.{mask2}.{mask3}.{mask4}" + "\n")
                    log = Log(target=dev.ip_address, action='cmd(Delete IP Address)', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                time.sleep(2)
                output = conn.recv(65535)
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(output.decode())
                result = '\n'.join(result)
                
                return render(request, 'result.html', {'result':result})
            except Exception as e:
                return ip_except(request, e, dev, setOrDel)
                
        elif additional_attr == 'three':
            try:
                var = request.session.get('device')
                interface = request.POST.get("interface")
                ip = request.POST.get("ip")
                ip2 = request.POST.get("ip2")
                ip3 = request.POST.get("ip3")
                ip4 = request.POST.get("ip4")
                mask = request.POST.get("mask")
                setOrDel = request.POST.get("setOrDel")
                
                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                addedOrRemoved = None
                if(setOrDel == 'set'):
                    stdin, stdout, stderr = ssh_client.exec_command(f"/ip address add address={ip}.{ip2}.{ip3}.{ip4}/{mask} interface={interface}")
                    log = Log(target=dev.ip_address, action='cmd(Set IP Address)', status='Success', time=datetime.now(), messages="No Error")
                    addedOrRemoved = True
                else:
                    stdin, stdout, stderr = ssh_client.exec_command(f'/ip address remove [/ip address find address="{ip}.{ip2}.{ip3}.{ip4}/{mask}" interface={interface}]')
                    log = Log(target=dev.ip_address, action='cmd(Delete IP Address)', status='Success', time=datetime.now(), messages="No Error")
                    addedOrRemoved = False
                log.save()
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(stdout.read().decode())
                result = '\n'.join(result)
                
                context = {
                    'result' : result,
                    'ip_address' : f'{ip}.{ip2}.{ip3}.{ip4}',
                    'interface' : interface,
                    'addedOrRemoved' : addedOrRemoved,
                }
                return render(request, 'result.html', context)
            except Exception as e:
                return ip_except(request, e, dev, setOrDel)
    else:
        devices = Device.objects.all()
        context = {
            'devices' : devices,
        }
        return render(request, 'config_ip/config_ip.html', context)

def ip_except(request, e, dev, setOrDel=None):
    if(setOrDel):
        if(setOrDel == 'set'):
            log = Log(target=dev.ip_address, action='cmd(Set IP Address)', status='Error', time=datetime.now(), messages=e)
        else:
            log = Log(target=dev.ip_address, action='cmd(Delete IP Address)', status='Error', time=datetime.now(), messages=e)
        log.save()
    devices = Device.objects.all()
    context = {
        'devices' : devices,
        'error_text' : 'there was ssh error connection with the IP: ',
        'error_ip' : dev.ip_address,
    }
    return render(request, 'config_ip/config_ip.html', context)
