# Checks to make sure that RDP is enabled and running on the Agent machine.
# Returns "not found" if RDP is disabled in the registry
# Returns "not running" if the service is not running

import os
import re
import psutil
from argparse import ArgumentParser
import subprocess
from os.path import join
from winreg import *
Registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
aKey = "System\CurrentControlSet\Control\Terminal Server"
key = OpenKey(Registry, aKey)
disabled_reg = QueryValueEx(key, "fDenyTSConnections")
disabled_reg = disabled_reg[0]
running = False
process_name = "Remote Desktop Services"

proc = subprocess.Popen("net start", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
for line in proc.stdout:
    if(process_name in str(line)):
        running = True


if (disabled_reg):
    print("not found")
elif(running==False):
    print("not running")
else:
    print("Okay")
