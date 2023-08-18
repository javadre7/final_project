from django.shortcuts import render, get_object_or_404
from network_automation.models import Device, Log
import paramiko, time
from datetime import datetime

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
                conn.send('tclsh\r')
                while not conn.recv_ready():
                    time.sleep(2)

                conn.send('foreach address {\r')
                while not conn.recv_ready():
                    time.sleep(2)

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
                        else:
                            conn.send(f'{i}}} {{ ping $address repeat {repeat} timeout {timeout} size {size}\r}}\r')
                            while not conn.recv_ready():
                                time.sleep(2)
                log = Log(target=dev.ip_address, action=f'cmd(tcl_ping)', status='Success', time=datetime.now(), messages="No Error")
                log.save()
                time.sleep(5)

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