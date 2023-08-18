from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime

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
                des = request.POST.get('des')
                des2 = request.POST.get('des2')
                des3 = request.POST.get('des3')
                des4 = request.POST.get('des4')
                if(request.POST.get('src') != ''):
                    src = request.POST.get('src')
                    src2 = request.POST.get('src2')
                    src3 = request.POST.get('src3')
                    src4 = request.POST.get('src4')
                repeat = request.POST.get('repeat')
                size = request.POST.get('size')
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

                time.sleep(4)
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
                des = request.POST.get('des')
                des2 = request.POST.get('des2')
                des3 = request.POST.get('des3')
                des4 = request.POST.get('des4')
                if(request.POST.get('src') != ''):
                    src = request.POST.get('src')
                    src2 = request.POST.get('src2')
                    src3 = request.POST.get('src3')
                    src4 = request.POST.get('src4')
                count = request.POST.get('count')
                size = request.POST.get('size')
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
