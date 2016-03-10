#!/usr/bin/python
#This is the test Agent for CABS on Windows

import socket, ssl
import sys
import os
import subprocess
import re
from sched import scheduler
from time import time, sleep
try:
    import psutil
except:
    psutil = None

import win32serviceutil
import win32service
import win32event
import servicemanager


ERR_GET_STATUS = -1
STATUS_PS_NOT_FOUND = 0
STATUS_PS_NOT_RUNNING = 1
STATUS_PS_NOT_CONNECTED = 2
STATUS_PS_OK = 3


settings = {}

def heartbeat():
    try:
        p = subprocess.Popen(["C:\\Windows\\Sysnative\\query.exe","user"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except:
        p = subprocess.Popen(["C:\\Windows\\system32\\query.exe","user"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    output, err = p.communicate()
    userlist = set()
    for i in range(1,len(output.split('\r\n'))-1):
        user = output.split('\r\n')[i].split()[0]
        if user.startswith(">"):
            user = user[1:]
        userlist.add(user)

    tellServer(userlist)

def tellServer(userlist):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((settings.get("Host_Addr"), int(settings.get("Agent_Port"))))
        if settings.get("Process_Listen") is not None and settings.get("Process_Listen") != 'None':
            content = "spr:" + settings.get("Process_Listen") + str(getStatus()) + ":" + settings.get("Hostname")
        else:
            content = "sr:" + settings.get("Hostname")
        for user in userlist:
            content += ":{0}".format(user)
        content += "\r\n"
        if (settings.get("SSL_Cert") is None) or (settings.get("SSL_Cert") == 'None'):
            s_wrapped = s 
        else:
            ssl_cert = os.path.join(settings.get("Directory"), settings.get("SSL_Cert"))
            s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=ssl_cert, ssl_version=ssl.PROTOCOL_SSLv23)
        
        s_wrapped.sendall(content)      
    except Exception as e:
        print "Could not connect to {0}:{1} because {2}".format(settings.get("Host_Addr"), settings.get("Agent_Port"), e)

def getStatus():
    #get the status of a process that matches settings.get("Process_Listen")
    #then check to make sure it has at least one listening conection
    #on windows, you can't search processes by yourself, so Popen "tasklist" to try to find the pid for the name
    #then use psutil to view the connections associated with that
    if not settings.get("Process_Listen") or psutil is None:
        return ERR_GET_STATUS
     
    #We really need admin privledges for this

    process = None
    
    try:
        p = psutil.Popen("tasklist", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        l_start = out.find(settings.get("Process_Listen"))
        l_end = out.find('\n', l_start)
        m = re.search(r"\d+", out[l_start: l_end])
        if m is None:
            return STATUS_PS_NOT_FOUND
        process = psutil.Process(int(m.group(0)))
    except:
        return ERR_GET_STATUS
        
    if process is None:
        return STATUS_PS_NOT_FOUND
    
    try:
        if not process.is_running():
            return STATUS_PS_NOT_RUNNING
        connections = False
        for conn in process.connections():
            if conn.status in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT, psutil.CONN_SYN_RECV, psutil.CONN_LISTEN]:
                connections = True
        if not connections:
            return STATUS_PS_NOT_CONNECTED
        else:
            return STATUS_PS_OK
    except:
        return ERR_GET_STATUS


def readConfigFile():
    #open the .conf file and return the variables as a dictionary
    global settings
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(os.path.abspath(sys.executable))
    elif __file__:
        application_path = os.path.dirname(os.path.abspath(__file__))
    settings["Directory"] = application_path
    
    if os.path.isfile(os.path.join(application_path, 'CABS_agent.conf')):
        filelocation = os.path.join(application_path, 'CABS_agent.conf')
    else:
        settings["Directory"] = '\\Program Files\\CABS\\Agent'
        filelocation = '\\Program Files\\CABS\\Agent' + '\\CABS_agent.conf'
        if not os.path.isfile(filelocation):
            settings["Directory"] = '\\Program Files (x86)\\CABS\\Agent'
            filelocation = '\\Program Files (x86)\\CABS\\Agent' + '\\CABS_agent.conf'
    with open(filelocation, 'r') as f:
        for line in f:
            line = line.strip()
            if (not line.startswith('#')) and line:
                try:
                    (key,val) = line.split(':\t',1)
                except:
                    print "Warning : Check .conf syntax"
                    try:
                        (key,val) = line.split(None,1)
                        key = key[:-1]
                    except:
                        key = line
                        key = key.strip()
                        key = key[:-1]
                        val = ''
                settings[key] = val
        f.close()
    #insert default settings for all not specified
    if not settings.get("Host_Addr"):
        settings["Host_Addr"] = 'localhost'
    if not settings.get("Agent_Port"):
        settings["Agent_Port"] = 18181
    if not settings.get("SSL_Cert"):
        settings["SSL_Cert"] = None
    if not settings.get("Interval"):
        settings["Interval"] = 120
    if not settings.get("Hostname"):
        settings["Hostname"] = None

    if (settings.get("Hostname") is None) or (settings.get("Hostname") == 'None'):
        #If we want a fqdn we can use socket.gethostbyaddr(socket.gethostname())[0]
        settings["Hostname"] = socket.gethostname()

class AgentService(win32serviceutil.ServiceFramework):
    #Special thanks to drmalex07 for his example python service code on github
    _svc_name_ = "CABS_Agent-Service"
    _svc_display_name_ = "CABS Agent Service"
    _svc_description_ = "The Agent reporting to the CABS Broker"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.stop_requested = False
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.stop_requested = True
    
    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.main()
    
    def runHeartbeat(self):
        #check flags
        if self.stop_requested:
            print "Stop signal received"
            sys.exit()
        else:
            heartbeat()

    def main(self):
        readConfigFile()
        self.s = scheduler(time, sleep)
        #read config for time interval, in seconds
        print "Starting. Pulsing every {0} seconds.".format(settings.get("Interval"))
        while True:
            self.s.enter(int(settings.get("Interval")), 1, self.runHeartbeat, ())
            self.s.run()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(AgentService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(AgentService)
