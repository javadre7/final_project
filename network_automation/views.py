from django.shortcuts import render, get_object_or_404, redirect #
from .models import Device, Log #
import paramiko, time # paramiko , time.sleep
from datetime import datetime #

import subprocess, json #

import re #

#
from .functions import home_devices

def home(request):
    return home_devices.home(request)

def devices(request):
    return home_devices.devices(request)

#
from .functions.manual_config import config, verify_config

def configure(request):
    return config.configure(request)

def verify_configure(request):
    return verify_config.verify_configure(request)

#
from .functions.readymade_commands import ping as p

def ping(request):
    return p.ping(request)

#
from .functions.readymade_commands import tcl_ping as tcl

def tcl_ping(request):
    return tcl.tcl_ping(request)

#
from .functions.readymade_commands import config_ip as c_ip

def config_ip(request):
    return c_ip.config_ip(request)

#
from .functions.readymade_commands import ssh_telnet as s_t

def ssh_telnet(request):
    return s_t.ssh_telnet(request)

#
from .functions.readymade_commands import mikrotik_command as mikrotik

def mikrotik_command(request, cmd):
    return mikrotik.mikrotik_command(request, cmd)

def mikrotik_command_1(request):
    return mikrotik_command(request, "interface print")

def mikrotik_command_2(request):
    return mikrotik_command(request,"ip address print")

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

#
from .functions.readymade_commands import cisco_command as cisco

def cisco_command(request, cmd):
    return cisco.cisco_command(request, cmd)

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

#
from .functions.log import log as l

def log(request):
    return l.log(request)

#
from .functions.backup_restore import backup

def backup_devices(request):
    return backup.backup_devices(request)

def backup_logs(request):
    return backup.backup_logs(request)

#
from .functions.backup_restore import restore

def restore_devices(request):
    return restore.restore_devices(request)

def restore_logs(request):
    return restore.restore_logs(request)

#
from .functions.delete_obj import delete_obj

def delete_devices(request):
    return delete_obj.delete_devices(request)

def delete_logs(request):
    return delete_obj.delete_logs(request)