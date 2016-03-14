#!/usr/bin/python2
#This is the test Agent for CABS for linux

# Workaround until a bugfix in pyinstaller gets released on pypi.
# See https://github.com/pyinstaller/pyinstaller/commit/f788dec36b8d55f4518881be9f4188ad865306ec
import socket, ssl
import sys
import os
import subprocess
import re
import signal
import traceback
import logging
from sched import scheduler
from time import time, sleep
from threading import Thread, Timer

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.ssl import Certificate, PrivateCertificate
from twisted.internet import reactor, endpoints
from twisted.protocols.basic import LineOnlyReceiver

logfile = os.path.join(os.getenv("APPDATA"), "cabsagent.log")
print "logfile: " + logfile
logging.basicConfig(filename=logfile, level=logging.DEBUG, format='%(asctime)s %(message)s')

try:
    import psutil
except:
    logging.warning("warning: couldn't import psutil. Process monitoring not available.")
    psutil = None

ERR_GET_STATUS = -1
STATUS_PS_NOT_FOUND = 0
STATUS_PS_NOT_RUNNING = 1
STATUS_PS_NOT_CONNECTED = 2
STATUS_PS_OK = 3

settings = {}
#global heartbeat_pid
requestStop = False

if os.name == "posix":
    def user_list():
        p = subprocess.Popen(["who"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        lines = output.split('\n')
        userlist = set()
        for line in lines:
            try:
                userlist.add(line.split()[0])
            except:
                pass
        return userlist

    def find_process():
        #assume a platform where we can just search with psutil
        for ps in psutil.process_iter():
            try:
                if ps.name() == settings.get("Process_Listen"):
                    return ps
            except:
                #we probably dont have permissions to access the ps.name()
                pass

    def reboot():
        subprocess.call(["shutdown", "-r", "now"])

    def restart():
        subprocess.call(["init", "2"])
        Timer(10, subprocess.call, (["init", "5"],)).start()
        #subprocess.call(["init", "5"])
else:
    assert os.name == "nt"
    #import win32service
    #import win32event
    #import servicemanager
    import win32api
    import win32serviceutil
    from getpass import getuser

    def user_list():
        return [getuser()]

    def find_process():
        p = psutil.Popen("tasklist", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
        out, err = p.communicate()
        l_start = out.find(settings.get("Process_Listen"))
        l_end = out.find('\n', l_start)
        m = re.search(r"\d+", out[l_start: l_end])
        if m is None:
            return None
        return  psutil.Process(int(m.group(0)))

    #def heartbeat_loop():
    #    if len(sys.argv) == 1:
    #        servicemanager.Initialize()
    #        servicemanager.PrepareToHostSingle(AgentService)
    #        servicemanager.StartServiceCtrlDispatcher()
    #    else:
    #        win32serviceutil.HandleCommandLine(AgentService)

    def restart():
        logging.info("restarting")
        if settings["Process_Listen"] is None:
            logging.warning("no process to restart")
            return
        #print "win32serviceutil.RestartService({})".format(settings["Process_Listen"])
        win32serviceutil.RestartService(settings["Process_Listen"].rstrip(".exe"))

    def reboot():
        logging.info("rebooting")
        win32api.InitiateSystemShutdown(None, None, 0, 1, 1)

    def stop():
        requestStop = True
        reactor.callFromThread(reactor.stop)

def heartbeat_loop():
    s = scheduler(time, sleep)
    #read config for time interval, in seconds
    logging.info("Starting. Pulsing every {0} seconds.".format(settings.get("Interval")))
    while True:
        if requestStop:
            break
        s.enter(int(settings.get("Interval")), 1, heartbeat, ())
        s.run()

def heartbeat():
    userlist = user_list()
    if settings.get("Process_Listen") is not None and psutil is not None:
        content = "spr:" + settings.get("Process_Listen") + str(getStatus()) + ":" + \
                    settings.get("Hostname")
    else:
        content = "sr:" + settings.get("Hostname")
    for user in userlist:
        content += ":{0}".format(user)
    content += "\r\n"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((settings.get("Host_Addr"), int(settings.get("Agent_Port"))))
        if settings.get("Broker_Cert") is None:
            s_wrapped = s 
        else:
            s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=settings["Broker_Cert"], \
                        ssl_version=ssl.PROTOCOL_SSLv23)
        
        s_wrapped.sendall(content)
        logging.info("Told server " + content)
    except:
        traceback.print_exc()

def getStatus():
    #get the status of a process that matches settings.get("Process_Listen")
    #then check to make sure it has at least one listening conection
    #on windows, you can't search processes by yourself, so Popen "tasklist" to try to find the pid for the name
    #then use psutil to view the connections associated with that
    #if not settings.get("Process_Listen") or psutil is None:
    #    return ERR_GET_STATUS
     
    #We really need admin privledges for this
    #try:
    assert psutil is not None
    process = find_process()
    if process is None:
        return STATUS_PS_NOT_FOUND
    if not process.is_running():
        return STATUS_PS_NOT_RUNNING
    #connections = False
    for conn in process.connections():
        if conn.status in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT,
                           psutil.CONN_SYN_RECV, psutil.CONN_LISTEN]:
            return STATUS_PS_OK
            #connections = True
    return STATUS_PS_NOT_CONNECTED
    #if not connections:
    #    return STATUS_PS_NOT_CONNECTED
    #else:
    #    return STATUS_PS_OK
    #except:
    #    return ERR_GET_STATUS

class CommandHandler(LineOnlyReceiver):
    """Recognized commands:
    restart_rgsender
    reboot
    """
    def lineReceived(self, line):
        command = line.strip()
        logging.info("received command: " + command)
        if command == "restart":
            restart()
        elif command == "reboot":
            reboot()

def start_ssl_cmd_server():
    with open(settings["Agent_Cert"], 'r') as certfile:
        certdata = certfile.read()
    if settings["Agent_Priv_Key"] != settings["Agent_Cert"]:
        with open(settings.get("Agent_Priv_Key"), 'r') as keyfile:
            certdata += keyfile.read()
    with open(settings.get("Broker_Cert"), 'r') as f:
        authdata = f.read()
    certificate = PrivateCertificate.loadPEM(certdata)
    authority = Certificate.loadPEM(authdata)
    factory = Factory.forProtocol(CommandHandler)
    reactor.listenSSL(int(settings.get("Command_Port")), factory, certificate.options(authority))

def readConfigFile():
    global settings
    settings = { "Host_Addr":'localhost',
                 "Agent_Port":18182,
                 "Command_Port":18185,
                 "Cert_Dir":"/usr/share/cabsagent/",
                 "Broker_Cert":None,
                 "Agent_Cert":None,
                 "Agent_Priv_Key":None,
                 "Interval":6,
                 "Process_Listen":None,
                 "Hostname":None }

    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(os.path.abspath(sys.executable))
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    filelocation = os.path.join(application_path, 'cabsagent.conf')
    with open(filelocation, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                continue
            try:
                key, val = [word.strip() for word in line.split(':', 1)]
            except ValueError:
                logging.warning("Warning: unrecognized setting: " + line)
                continue
            if key not in settings:
                logging.warning("Warning: unrecognized setting: " + line)
                continue
            settings[key] = val
        f.close()

    for key in ("Broker_Cert", "Agent_Cert"):
        if settings[key] is not None and not os.path.isabs(settings[key]):
            settings[key] = os.path.join(settings["Cert_Dir"], settings[key])
    if settings["Agent_Priv_Key"] is None:
        settings["Agent_Priv_Key"] = settings["Agent_Cert"]

    if settings["Hostname"] is None:
        #If we want a fqdn we can use socket.gethostbyaddr(socket.gethostname())[0]
        settings["Hostname"] = socket.gethostname()

def stop():
    requestStop = True
    reactor.callFromThread(reactor.stop)

def start():
    readConfigFile()
    t = Thread(target=heartbeat_loop)
    t.daemon = True
    t.start()

    if settings.get("Agent_Priv_Key") is None:
        endpoint = endpoints.TCP4ServerEndpoint(reactor, int(settings.get("Command_Port")))
        endpoint.listen(Factory.forProtocol(CommandHandler))
    else:
        start_ssl_cmd_server()
    logging.info("running the reactor")
    reactor.run()

if __name__ == "__main__":
    start()
