import os
import sys
import time

import psutil
import socket

import re
from pathlib import Path

from retrying import retry
from wrapt_timeout_decorator import *

from rcon.source import Client

rcon_host = "localhost"
rcon_port = 25575
rcon_password = "1p2o3i4u"

CAPTURE_TPS = True
CAPTURE_TPS_WITH_DEBUG = False

server_version = 'spigot_1.12.2'
server_debug_path = f'../mc_server/{server_version}/debug'


def process_rcon_message(message: str):
    result = ''
    i= 0
    while i < len(message):
        if message[i] == '§':
            i += 2
        else:
            result += message[i]
            i += 1
    return result

def get_mspt_from_rcon_message(message: str):
    numbers = re.findall(r'\b\d+\.*\d*\b', message)
    mspt = float(numbers[3])
    return mspt

# def get_tps_from_debug_file(filename: str):
#     text = Path(filename).read_text()
#     ms = re.findall(r'\b\d+\.*\d*\b', text)[0]
#     numbers = re.findall(r'\b\d+\.*\d*\b', text)
#     ms, tick = float(numbers[0]), float(numbers[1])
#     return tick / ms * 1000

def get_tps_from_debug_response(response: str):
    numbers = re.findall(r'\b\d+\.*\d*\b', response)
    seconds, ticks = float(numbers[0]), float(numbers[1])
    return ticks / seconds

@retry(wait_fixed=1000)
@timeout(2)
def start_debug():
    print("trying to start debug")
    with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
        response = client.run("debug start")
    print(response)
    return response

@retry(wait_fixed=1000)
@timeout(2)
def stop_debug_and_read_result():
    print("trying to stop debug")
    with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
        response = client.run("debug stop")
    print(response)
    tps = get_tps_from_debug_response(response)
    return tps


@retry(wait_fixed=1000)
@timeout(2)
def get_mspt():
    with Client(rcon_host, rcon_port, passwd=rcon_password) as client:
        response = client.run("mspt")
    cleaned_response = process_rcon_message(response)
    mspt = get_mspt_from_rcon_message(cleaned_response)   
    return mspt

def key_or_val(li, key, value, header):
    if header:
        li.append(key)
    else:
        li.append(value)


if __name__ == "__main__":
    logfile = sys.argv[1]
    pid = int(sys.argv[2])
    p = psutil.Process(pid)
    first = True

    for f in os.listdir(server_debug_path):
        os.remove(os.path.join(server_debug_path, f))

    with open(logfile, "w+") as fout:
        
        if CAPTURE_TPS and CAPTURE_TPS_WITH_DEBUG:
            start_debug()
        time.sleep(1)

        while True:
            counters = []
            
            key_or_val(counters, "timestamp", f"{time.time() * 1000}", first)

            
            sys_counters = p.as_dict()
            for k in sorted(sys_counters):
                v = sys_counters[k]
                if k in ["environ", "cmdline", "connections", "open_files", "memory_maps", "threads", "cpu_affinity"]:
                    continue
                elif k in ["gids", "memory_info", "uids", "num_ctx_switches", "cpu_times", "io_counters", "ionice",
                           "memory_full_info"]:
                    vdict = v._asdict()
                    for sk in sorted(vdict):
                        sv = vdict[sk]
                        key_or_val(counters, f"proc.{k}.{sk}", f"{sv}", first)
                else:
                    key_or_val(counters, f"proc.{k}", f"{v}", first)

            net = psutil.net_io_counters(pernic=True)
            for device in sorted(net):
                net_device = net[device]
                key_or_val(counters, f"net.bytes_sent.{device}", f"{net_device.bytes_sent}", first)
                key_or_val(counters, f"net.bytes_recv.{device}", f"{net_device.bytes_recv}", first)
                key_or_val(counters, f"net.packets_sent.{device}", f"{net_device.packets_sent}", first)
                key_or_val(counters, f"net.packets_recv.{device}", f"{net_device.packets_recv}", first)
                key_or_val(counters, f"net.errin.{device}", f"{net_device.errin}", first)
                key_or_val(counters, f"net.errout.{device}", f"{net_device.errout}", first)
                key_or_val(counters, f"net.dropin.{device}", f"{net_device.dropin}", first)
                key_or_val(counters, f"net.dropout.{device}", f"{net_device.dropout}", first)

            disks = psutil.disk_io_counters(perdisk=True)
            for disk in sorted(disks):
                disks_disk = disks[disk]
                key_or_val(counters, f"disk.read_count.{disk}", f"{disks_disk.read_count}", first)
                key_or_val(counters, f"disk.read_bytes.{disk}", f"{disks_disk.read_bytes}", first)
                key_or_val(counters, f"disk.write_count.{disk}", f"{disks_disk.write_count}", first)
                key_or_val(counters, f"disk.write_bytes.{disk}", f"{disks_disk.write_bytes}", first)

            cputimes = psutil.cpu_times(percpu=False)
            cpudict = cputimes._asdict()
            for sk in sorted(cpudict):
                sv = cpudict[sk]
                key_or_val(counters, f"cpu.{sk}", f"{sv}", first)

            cpupercent = psutil.cpu_percent(percpu=False)
            key_or_val(counters, f"cpu.percent", f"{cpupercent}", first)

            cpufreq = psutil.cpu_freq()
            key_or_val(counters, f"cpu.freq.current", f"{cpufreq.current}", first)
            key_or_val(counters, f"cpu.freq.min", f"{cpufreq.min}", first)
            key_or_val(counters, f"cpu.freq.max", f"{cpufreq.max}", first)

            cpus = psutil.cpu_stats()
            key_or_val(counters, f"cpu.ctx_switches", f"{cpus.ctx_switches}", first)
            key_or_val(counters, f"cpu.interrupts", f"{cpus.interrupts}", first)
            key_or_val(counters, f"cpu.soft_interrupts", f"{cpus.soft_interrupts}", first)
            key_or_val(counters, f"cpu.syscalls", f"{cpus.syscalls}", first)
            
            if CAPTURE_TPS:
                if CAPTURE_TPS_WITH_DEBUG:
                    key_or_val(counters, "mspt", f"{stop_debug_and_read_result()}", first)
                    start_debug()
                else:
                    mspt = get_mspt()
                    tps = min(20, 1000 / mspt)
                    print(mspt, tps)
                    key_or_val(counters, "mspt", f"{mspt}", first)
                    key_or_val(counters, "tps", f"{tps}", first)

            fout.write("\t".join(counters))
            fout.write(os.linesep)
            fout.flush()
            first = False
            time.sleep(1)
