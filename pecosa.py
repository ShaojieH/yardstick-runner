import os
import sys
import time

import psutil
import socket
import mcrcon

import re

rcon_host = "localhost"
rcon_port = 25575
rcon_password = "1p2o3i4u"

CAPTURE_MSPT = False

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((rcon_host, rcon_port))

mcrcon.login(sock, rcon_password)

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
    mspt = numbers[3]
    return mspt

def get_mspt():
    response = mcrcon.command(sock, "mspt")
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
    with open(logfile, "w+") as fout:
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


            if CAPTURE_MSPT:
                key_or_val(counters, "mspt", f"{get_mspt()}", first)

            fout.write("\t".join(counters))
            fout.write(os.linesep)
            fout.flush()
            first = False
            time.sleep(1)
