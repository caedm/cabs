#!/usr/bin/python2 -u
#This is the test Agent for CABS for linux

# Workaround until a bugfix in pyinstaller gets released on pypi.
# See https://github.com/pyinstaller/pyinstaller/commit/f788dec36b8d55f4518881be9f4188ad865306ec
import socket, ssl
import sys
import os
import subprocess
from subprocess import check_output, check_call
import re
import signal
import traceback
from sched import scheduler
from time import time, sleep
from threading import Thread, Timer
import threading

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.ssl import Certificate, PrivateCertificate
from twisted.internet import reactor, endpoints
from twisted.protocols.basic import LineOnlyReceiver
from argparse import ArgumentParser
from os.path import isfile

try:
    import psutil
except:
    print("warning: couldn't import psutil. Process monitoring not available.")
    psutil = None

ERR_GET_STATUS = -1
STATUS_PS_NOT_FOUND = 0
STATUS_PS_NOT_RUNNING = 1
STATUS_PS_NOT_CONNECTED = 2
STATUS_PS_OK = 3

#global heartbeat_pid
requestStop = False

settings = { "Host_Addr":'broker',
             "Agent_Port":18182,
             "Command_Port":18185,
             "Cert_Dir":"/etc/ssl/certs",
             "Broker_Cert":None,
             "Agent_Cert":None,
             "Agent_Priv_Key":None,
             "Interval":1,
             "Process_Listen":None,
             "Hostname":"cabs.et.byu.edu" }
checks = []


def ps_check():
    # get the status of a process that matches settings.get("Process_Listen")
    # then check to make sure it has at least one listening conection on windows, you can't
    # search processes by yourself, so Popen "tasklist" to try to find the pid for the name
    # then use psutil to view the connections associated with that
    if not psutil:
        return "Okay"

    ps_name = settings.get("Process_Listen")
    process = find_process()
    if process is None:
        return ps_name + " not found"
    if not process.is_running():
        return ps_name + " not running"
    for conn in process.connections():
        if conn.status in [psutil.CONN_ESTABLISHED, psutil.CONN_SYN_SENT,
                psutil.CONN_SYN_RECV, psutil.CONN_LISTEN]:
            return "Okay"
    return ps_name + " not connected"

if os.name == "posix": #is this necessary?
    def user_list():
        p = subprocess.Popen(["who"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        if sys.version_info[0] < 3: #Make sure it is python2/3 compatible
            output = output.encode('utf-8')
        else:
            output = str(output, 'utf-8')
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


    def win_info(user, display):
        if argv.debug:
            template = ('0x01e00003 -1 0    {}  1024 24   rgsl-07 Top Expanded Edge Panel\n'
                    '0x01e00024 -1 0    1536 1024 24   rgsl-07 Bottom Expanded Edge Panel\n')
            return template.format('-48' if isfile('/tmp/no_panel') else '0')
        else:
            return check_output("script -c 'DISPLAY={} sudo -u {} wmctrl -lG' /dev/null"
                    "| grep -v Script".format(display, user), shell=True)

            # We can only check if there's a panel when someone is logged in. If the user logs out, we
    # want to remember that there wasn't a panel.
    no_panel = False
    def panel_check():
        global no_panel
        print('running panel check')
        graphical_users = [line.split() for line in check_output("who").split(b'\n')
                if b" :0" in line]
        if graphical_users:
            user = graphical_users[0][0]
            display = graphical_users[0][1]
            info = win_info(user, display).split('\n')
            y_coords = [line.split()[3] for line in info if "Top Expanded Edge Panel" in line]
            no_panel = any(int(coord) < 0 for coord in y_coords)
        elif no_panel and not user_list():
            reboot()

        return "no_panel" if no_panel else "Okay"

    checks.append(panel_check)

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
        print("restarting")
        if settings["Process_Listen"] is None:
            print("no process to restart")
            return
        #print("win32serviceutil.RestartService({})".format(settings["Process_Listen"]))
        win32serviceutil.RestartService(settings["Process_Listen"].rstrip(".exe"))

    def reboot():
        print("rebooting")
        win32api.InitiateSystemShutdown(None, None, 0, 1, 1)

    def stop():
        requestStop = True
        reactor.callFromThread(reactor.stop)

def heartbeat_loop():
    sched = scheduler(time, sleep)
    #read config for time interval, in seconds
    print("Starting heartbeat. Pulsing every {0} seconds.".format(settings.get("Interval")))
    while True:
        if requestStop:
            break
        sched.enter(int(settings.get("Interval")), 1, heartbeat, ())
        sched.run()

def heartbeat():
    content = "spr:{}:{}{}\r\n".format(getStatus(), settings["Hostname"],
            "".join(':' + user for user in user_list()))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1) #edited this to stop doubling up error
        
        if settings.get("Broker_Cert") is None:
            s_wrapped = s 
        else:
            #ssl.SSLContext.load_cert_chain(settings["Broker_Cert"])
            s_wrapped = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) 
            s_wrapped.check_hostname= False
            s_wrapped.load_verify_locations(settings["Broker_Cert"]) #edited this #might need ".load_cert_chain(settings["Broker_Cert"]
            s_wrapped = s_wrapped.wrap_socket(s,False,True,True,None,None)
            s_wrapped.connect((settings.get("Host_Addr"), int(settings.get("Agent_Port"))))
            if sys.version_info[0] < 3: #Make sure it is python2/3 compatible
                s_wrapped.send(content)
            else:
                s_wrapped.send(bytes("Good job", 'utf-8'))
        print("Told server " + content)
    except:
        traceback.print_exc()

def getStatus():
    if argv.debug and isfile('/tmp/oldstatus'):
        return "rgsender3"

    problems = [result for result in [func() for func in checks]
            if result != "Okay"]
    return ",".join(problems) if problems else "Okay"

class CommandHandler(LineOnlyReceiver):
    """Recognized commands:
    restart_rgsender
    reboot
    """
    def lineReceived(self, line):
        command = line.strip()
        print("received command: " + command)
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
    if isfile(argv.config):
        with open(argv.config, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                try:
                    key, val = [word.strip() for word in line.split(':', 1)]
                except ValueError:
                    print("Warning: unrecognized setting: " + line)
                    continue
                if key not in settings:
                    print("Warning: unrecognized setting: " + line)
                    continue
                settings[key] = val
            f.close()
        print(settings)
            

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

def startHeartbeat():
    readConfigFile()
    global checks
    if settings['Process_Listen'] and psutil:
        checks.append(ps_check)
    t = Thread(target=heartbeat_loop, name="heartbeat")
    t.start()

def checkHeartbeat():
    for thread in threading.enumerate():
        if thread.name == "heartbeat":
            print("Heartbeat is still running")
            return
    print("Heartbeat thread stopped, restarting heartbeat")
    startHeartbeat()
        
def heartbeatSupervisor():
    s = scheduler(time, sleep)
    threadCountInterval = 20
    print("Starting heartbeat supervisor. Checking every {0} seconds.".format(threadCountInterval))
    while True:
        if requestStop:
            break
        s.enter(threadCountInterval, 1, checkHeartbeat, ())
        s.run()

def startHeartbeatSupervisor():
    t_count = Thread(target=heartbeatSupervisor, name="supervisor")
    t_count.daemon = True
    t_count.start()

def start():
    application_path = os.path.dirname(os.path.abspath(
        sys.executable if getattr(sys, 'frozen', False) else __file__))
    default_config = os.path.join(application_path, 'cabsagent.conf') #application path is the directory of this
    global argv
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--config', default=default_config)
    argv = parser.parse_args()

    startHeartbeat()
    startHeartbeatSupervisor()


    if settings.get("Agent_Priv_Key") is None:
        endpoint = endpoints.TCP4ServerEndpoint(reactor, int(settings.get("Command_Port")))
        endpoint.listen(Factory.forProtocol(CommandHandler))
    else:
        start_ssl_cmd_server()
    print("Running the reactor")
    reactor.run() #Error here

if __name__ == "__main__":
    start()
