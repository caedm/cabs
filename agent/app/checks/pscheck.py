#!/usr/bin/python2
# get the status of a process that matches settings.get("Process_Listen")
# then check to make sure it has at least one listening conection on windows, you can't
# search processes by yourself, so Popen "tasklist" to try to find the pid for the name
#onf then use psutil to view the connections associated with that

import os
import psutil
import re
from argparse import ArgumentParser
import subprocess
from os.path import join

if os.name == "posix":
    default = "rgsender"

    def find_process(ps_name):
        for ps in psutil.process_iter():
            try:
                if ps.name() == ps_name:
                    return ps
            except:
                # we probably don't have permissions to access the ps.name()
                pass

else:
    default = "rgsender.exe"

    def find_process(ps_name):
        p = psutil.Popen("tasklist", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        out, err = p.communicate()
        l_start = out.find(ps_name)
        l_end = out.find('\n', l_start)
        m = re.search(r"\d+", out[l_start: l_end])
        if m is None:
            return None
        return  psutil.Process(int(m.group(0)))

def status(ps_name):
    process = find_process(ps_name)
    if process is None:
        return ps_name + " not found"
    if not process.is_running():
        return ps_name + " not running"
    for conn in process.connections():
        if conn.status in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT,
                           psutil.CONN_SYN_RECV, psutil.CONN_LISTEN]:
            return "Okay"
    return ps_name + " not connected"

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("process", nargs="?", default=default)
    args = parser.parse_args()

    print status(args.process)
