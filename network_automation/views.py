from django.shortcuts import render, HttpResponse, get_object_or_404, redirect
from .models import Device, Log
import paramiko, time
from datetime import datetime

import subprocess, json
from django.http import HttpResponse

import re

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

def verify_config(request):
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
                        # time.sleep(1)
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

def mikrotik_command_1(request):
    return mikrotik_command(request,"interface print")

def mikrotik_command_2(request):
    return mikrotik_command(request,"/ip address print")

def mikrotik_command_3(request):
    return mikrotik_command(request,"ip route print")

def mikrotik_command_4(request):
    return mikrotik_command(request,"routing ospf neighbor print")

def mikrotik_command_5(request):
    return mikrotik_command(request,"routing bgp peer print")

def mikrotik_command_6(request):
    return mikrotik_command(request,"routing rip neighbor print")

def mikrotik_command_7(request):
    return mikrotik_command(request,"system reboot")

def mikrotik_command_8(request):
    return mikrotik_command(request,"routing ospf network print")

def mikrotik_command_9(request):
    return mikrotik_command(request,"routing bgp network print")

def mikrotik_command_10(request):
    return mikrotik_command(request,"routing rip network print")

def cisco_command(request, cmd):
    if request.method == 'POST':
        result = []
        selected_device_id = request.POST.getlist('device')
        for x in selected_device_id:
            try:
                dev = get_object_or_404(Device, pk=x)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)

                conn = ssh_client.invoke_shell()
                conn.send('terminal length 0\n')
                result.append(f"[[[Result on {dev.ip_address}]]]")
                conn.send(cmd + "\n")
                time.sleep(2)
                output = conn.recv(65535)
                result.append(output.decode())

                log = Log(target=dev.ip_address, action=f'cmd({cmd})', status='Success', time=datetime.now(), messages="No Error")
                log.save()
            except Exception as e:
                log = Log(target=dev.ip_address, action=f'cmd({cmd})', status='Error', time=datetime.now(), messages=e)
                log.save()
    
        result = '\n'.join(result)
        return render(request, 'result.html', {'result':result})

    else:
        devices = Device.objects.filter(vendor='cisco')
        context = {
            'devices': devices,
            'mode' : f'Sending "{cmd}" command to CISCO Device',
            'model' : 'CISCO'
        }
        
        return render(request, 'command.html', context)

def cisco_command_1(request):
    return cisco_command(request, "show ip interface brief")

def cisco_command_2(request):
    return cisco_command(request, "show running-config")

def cisco_command_3(request):
    return cisco_command(request, "show ip route")

def cisco_command_4(request):
    return cisco_command(request, "show ip ospf neighbor")

def cisco_command_5(request):
    return cisco_command(request, "show ip bgp summary")

def cisco_command_6(request):
    return cisco_command(request, "show ip rip database")

def cisco_command_7(request):
    return cisco_command(request, "copy running-config startup-config\n")

def cisco_command_8(request):
    return cisco_command(request, "write")

def cisco_command_9(request):
    return cisco_command(request, "show startup-config")

def cisco_command_10(request):
    return cisco_command(request, "show ip eigrp neighbors")

def cisco_command_11(request):
    return cisco_command(request, "show running-config | section router")

def cisco_command_12(request):
    return cisco_command(request, "show ip protocols")

def cisco_command_13(request):
    return cisco_command(request, "show ip access-list")

def cisco_command_14(request):
    return cisco_command(request, "show processes cpu")

def cisco_command_15(request):
    return cisco_command(request, "show processes cpu | ex 0.00")

# def cisco_command_16(request):
#     return cisco_command(request, "reload\r [confirm]\r")
    
def log(request):
    logs = Log.objects.all()

    context = {
        "logs": logs
    }

    return render(request, 'log.html', context)

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

def delete_devices(request):

    Device.objects.all().delete()

    return render(request, 'reset/delete_devices.html')

def delete_logs(request):

    Log.objects.all().delete()

    return render(request, 'reset/delete_logs.html')

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
    
                    for line in lines[3:]:                              # Skip the header rows
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
                    #Flags: D - dynamic, X - disabled, R - running, S - slave 
                    # #     NAME                                TYPE       ACTUAL-MTU L2MTU
                    # 0  R  ether1                              ether            1500
                    # 1  R  ether2                              ether            1500
                    # 2  R  ether3                              ether            1500
                    lines = second_element.split("\r\n")
                    #['Flags: D - dynamic, X - disabled, R - running, S - slave ', ' #     NAME                                TYPE       ACTUAL-MTU L2MTU', ' 0  R  ether1
                    #    ether            1500', ' 1  R  ether2                              ether            1500', ' 2  R  ether3                              ether            1500', '', '']
                    lines = [line.strip() for line in lines]
                    #['Flags: D - dynamic, X - disabled, R - running, S - slave', '#     NAME                                TYPE       ACTUAL-MTU L2MTU', '0  R  ether1
                    # ether            1500', '1  R  ether2                              ether            1500', '2  R  ether3                              ether            1500', '', '']
                    
                    index = next((i for i, line in enumerate(lines) if line.startswith('#     NAME')), None)
                    # simpler code:
                    # index = None
                    # for i, line in enumerate(lines):
                    #     if line.startswith('#     NAME'):
                    #         index = i
                    #         break
                    
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

def ping(request):
    if request.method == 'POST':
        additional_attr = request.POST.get('additional')
        if additional_attr == 'one':
            try:
                request.session['device'] = selected_device_id = request.POST.getlist('device')[0]
                dev = get_object_or_404(Device, pk = selected_device_id)
                device_model = dev.vendor.lower()

                if (device_model == 'cisco'):
                    return render(request, 'ping/ping_cisco.html')
                else:
                    return render(request, 'ping/ping_mikrotik.html')
            except Exception as e:
                return ping_except(request, e, dev, True)

        elif additional_attr == 'two':
            try:
                var = request.session.get('device')

                # destination - ip address of destintaion
                des = request.POST.get('des')
                des2 = request.POST.get('des2')
                des3 = request.POST.get('des3')
                des4 = request.POST.get('des4')
                # source (default=empty) - ip address of source
                if(request.POST.get('src') != ''):
                    src = request.POST.get('src')
                    src2 = request.POST.get('src2')
                    src3 = request.POST.get('src3')
                    src4 = request.POST.get('src4')
                # repeat (default=5) - number of ping request
                repeat = request.POST.get('repeat')
                # size (default=100) - bytes
                size = request.POST.get('size')
                # timeout (default=2) - sec
                timeout = request.POST.get('timeout')

                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                conn = ssh_client.invoke_shell()
                conn.send('terminal length 0\n')
                if(request.POST.get('src') != ''):
                    conn.send(f'ping {des}.{des2}.{des3}.{des4} repeat {repeat} timeout {timeout} size {size} source {src}.{src2}.{src3}.{src4}\n')    
                else:
                    conn.send(f'ping {des}.{des2}.{des3}.{des4} repeat {repeat} timeout {timeout} size {size}\n')
                log = Log(target=dev.ip_address, action=f'cmd(ping {des}.{des2}.{des3}.{des4})', status='Success', time=datetime.now(), messages="No Error")
                log.save()

                # int(repeat) + int(timeout)
                time.sleep(2)
                output = conn.recv(65535)
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(output.decode())
                result = '\n'.join(result)

                return render(request, 'result.html', {'result' : result})
            except Exception as e:
                return ping_except(request, e, dev, False, des, des2, des3, des4)
                
        elif additional_attr == 'three':
            try:
                var = request.session.get('device')
                # destination - ip address of destintaion
                des = request.POST.get('des')
                des2 = request.POST.get('des2')
                des3 = request.POST.get('des3')
                des4 = request.POST.get('des4')
                # source (default=empty) - ip address of source
                if(request.POST.get('src') != ''):
                    src = request.POST.get('src')
                    src2 = request.POST.get('src2')
                    src3 = request.POST.get('src3')
                    src4 = request.POST.get('src4')
                # count (default=5) - number of ping request
                count = request.POST.get('count')
                # size (default=100) - bytes
                size = request.POST.get('size')
                # interval (default=1) - sec
                interval = request.POST.get('interval')

                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                if(request.POST.get('src') != ''):
                    stdin, stdout, stderr = ssh_client.exec_command(f"ping {des}.{des2}.{des3}.{des4} count={count} size={size} interval={interval} src-address={src}.{src2}.{src3}.{src4}")
                else:
                    stdin, stdout, stderr = ssh_client.exec_command(f"ping {des}.{des2}.{des3}.{des4} count={count} size={size} interval={interval}")
                log = Log(target=dev.ip_address, action=f'cmd(ping {des}.{des2}.{des3}.{des4})', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(stdout.read().decode())
                result = '\n'.join(result)

                return render(request, 'result.html', {'result' : result})
            except Exception as e:
                return ping_except(request, e, dev, False, des, des2, des3, des4)
    else:
        devices = Device.objects.all()
        context = {
            'devices' : devices,
        }
        return render(request, 'ping/ping.html', context)

def ping_except(request, e, dev, first_form, des=None, des2=None, des3=None, des4=None):
    if (first_form == False):
        log = Log(target=dev.ip_address, action=f'cmd(ping {des}.{des2}.{des3}.{des4})', status='Error', time=datetime.now(), messages=e)
        log.save()
    devices = Device.objects.all()
    context = {
        'devices' : devices,
        'error_text' : 'there was ssh error connection with the IP: ',
        'error_ip' : dev.ip_address,
    }
    return render(request, 'ping/ping.html', context)


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

def tcl_ping(request):
    if request.method == 'POST':
        additional_attr = request.POST.get('additional')
        if additional_attr == 'one':
            try:
                request.session['device'] = selected_device_id = request.POST.getlist('device')[0]
                dev = get_object_or_404(Device, pk = selected_device_id)
                return render(request, 'tcl_ping/ping_cisco.html')
            except Exception as e:
                return tcl_ping_except(request, e, dev, True)
        else:
            try:
                var = request.session.get('device')
                array = request.POST['des'].splitlines()
                
                # source (default=empty) - ip address of source
                if(request.POST.get('src') != ''):
                    src = request.POST.get('src')
                    src2 = request.POST.get('src2')
                    src3 = request.POST.get('src3')
                    src4 = request.POST.get('src4')
                # repeat (default=5) - number of ping request
                repeat = request.POST.get('repeat')
                # size (default=100) - bytes
                size = request.POST.get('size')
                # timeout (default=2) - sec
                timeout = request.POST.get('timeout')

                dev = get_object_or_404(Device, pk = var)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=dev.ip_address, username=dev.username, password=dev.password, allow_agent=False, look_for_keys=False)
                conn = ssh_client.invoke_shell()
                conn.send('terminal length 0\n')
                conn.send('tclsh\r')

                # 1st way (did work as solution, but it is interesting that without my timer it is not going to work), my timer code must be below of log.save()
                # my timer code is not efficient bcaz it consider the worst case scenario (if ping not respond, it will late), so my code is:
                #   timer = int(timeout) * int(repeat) * no_of_ip
                #   time.sleep(timer)
                # his code:
                while not conn.recv_ready():
                    time.sleep(2)
                # 1st way better solution found: it is really nice, when u send command just let these 2 above lines run, if some destintaion ip not respond, then user will be informed, bcaz it will show incomplete result


                # 2nd way (did not work as solution)
                    # buff=''
                    # while '#' not in buff:
                    #     if conn.recv_ready():
                    #         response = conn.recv(65535).decode()
                    #         buff += response
                
                conn.send('foreach address {\r')
                while not conn.recv_ready():
                    time.sleep(2)

                no_of_ip = 0
                if(request.POST.get('src') != ''):
                    for c,i in enumerate(array):
                        if (c != array[len(array)-1]):
                            conn.send('{}\r'.format(i))
                            while not conn.recv_ready():
                                time.sleep(2)
                        else:
                            conn.send(f'{i}}} {{ ping $address repeat {repeat} timeout {timeout} size {size} source {src}.{src2}.{sr3}.{src4}\r}}\r')
                            while not conn.recv_ready():
                                time.sleep(2)
                else:
                    for c,i in enumerate(array):
                        if (c != len(array)-1):
                            conn.send(f'{i}\r')
                            while not conn.recv_ready():
                                time.sleep(2)
                            no_of_ip = no_of_ip + 1
                        else:
                            conn.send(f'{i}}} {{ ping $address repeat {repeat} timeout {timeout} size {size}\r}}\r')
                            while not conn.recv_ready():
                                time.sleep(2)
                            no_of_ip = no_of_ip + 1
                log = Log(target=dev.ip_address, action=f'cmd(tcl_ping)', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                
                # timer = int(timeout) * int(repeat) * no_of_ip
                # time.sleep(timer)

                # conn.send('tclquit\r')
                time.sleep(2)

                output = conn.recv(65535)
                result = []
                result.append(f'[[[Result on {dev.ip_address}]]]')
                result.append(output.decode())
                result = '\n'.join(result)

                return render(request, 'result.html', {'result' : result})
            except Exception as e:
                return tcl_ping_except(request, e, dev, False)
    else:
        devices = Device.objects.filter(vendor='cisco')
        context = {
            'devices' : devices,
        }
        return render(request, 'tcl_ping/ping.html', context)

def tcl_ping_except (request, e, dev, first_form):
    if (first_form == False):
        log = Log(target=dev.ip_address, action=f'cmd(tcl_ping)', status='Error', time=datetime.now(), messages=e)
        log.save()
    devices = Device.objects.filter(vendor='cisco')
    context = {
            'devices' : devices,
            'error_text' : 'there was ssh error connection with the IP: ',
            'error_ip' : dev.ip_address,
        }
    return render(request, 'tcl_ping/ping.html', context)