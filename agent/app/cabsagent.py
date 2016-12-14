#!/usr/bin/python2 -u
#This is the test Agent for CABS for linux

# Workaround until a bugfix in pyinstaller gets released on pypi.
# See https://github.com/pyinstaller/pyinstaller/commit/f788dec36b8d55f4518881be9f4188ad865306ec
import ctypes.util

import socket, ssl
import sys
import os
import subprocess
from subprocess import check_output, check_call, CalledProcessError
import re
import signal
import traceback
from sched import scheduler
from time import time, sleep
from threading import Thread, Timer

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.ssl import Certificate, PrivateCertificate
from twisted.internet import reactor, endpoints
from twisted.protocols.basic import LineOnlyReceiver
from argparse import ArgumentParser
from os.path import isfile, isabs, basename, join
import logging

log = logging.getLogger()
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())

ERR_GET_STATUS = -1
STATUS_PS_NOT_FOUND = 0
STATUS_PS_NOT_RUNNING = 1
STATUS_PS_NOT_CONNECTED = 2
STATUS_PS_OK = 3

requestStop = False

application_path = os.path.dirname(os.path.abspath(
                   sys.executable if getattr(sys, 'frozen', False) else __file__))
default_config = os.path.join(application_path, 'cabsagent.conf')
settings = { "Host_Addr":'broker',
             "Agent_Port":18182,
             "Command_Port":18185,
             "Cert_Dir":application_path,
             "Broker_Cert":None,
             "Agent_Cert":None,
             "Agent_Priv_Key":None,
             "Interval":1,
             "Process_Listen":None,
             "Hostname":None,
             "Checks_Dir":'checks',
             "Check_Scripts": ""}
DEBUG = False

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

    def reboot():
        log.info("rebooting")
        subprocess.call(["shutdown", "-r", "now"])

    def restart():
        subprocess.call(["init", "2"])
        Timer(10, subprocess.call, (["init", "5"],)).start()
        #subprocess.call(["init", "5"])
else:
    assert os.name == "nt"

    # Fix for another pyinstaller problem.
    import _cffi_backend

    import win32api
    import win32serviceutil

    def user_list():
        try:
            output = check_output(['query.exe', 'user'])
        except CalledProcessError as e:
            # query.exe returns 1 after successful execution. It was obviously written by a
            # Roman unfamiliar with the concept of 0.
            output = e.output
            
        userlist = set()
        for i in range(1,len(output.split('\r\n'))-1):
            user = output.split('\r\n')[i].split()[0]
            if user.startswith(">"):
                user = user[1:]
            userlist.add(user)
        return userlist

    def restart():
        log.info("restarting")
        if settings["Process_Listen"] is None:
            log.info("no process to restart")
            return
        #print "win32serviceutil.RestartService({})".format(settings["Process_Listen"])
        win32serviceutil.RestartService(settings["Process_Listen"].rstrip(".exe"))

    def reboot():
        log.info("rebooting")
        win32api.InitiateSystemShutdown(None, None, 0, 1, 1)

    def stop():
        requestStop = True
        reactor.callFromThread(reactor.stop)

def heartbeat_loop():
    s = scheduler(time, sleep)
    #read config for time interval, in seconds
    log.info("Starting. Pulsing every {0} seconds.".format(settings.get("Interval")))
    while not requestStop:
        s.enter(int(settings.get("Interval")), 1, heartbeat, ())
        s.run()

def heartbeat():
    log.info("doing a heartbeat")
    content = "spr:{}:{}{}\r\n".format(getStatus(), settings["Hostname"],
            "".join(':' + user for user in user_list()))
    log.info("content: {}".format(content))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((settings.get("Host_Addr"), int(settings.get("Agent_Port"))))
        if settings.get("Broker_Cert") is None:
            s_wrapped = s 
        else:
            s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=settings["Broker_Cert"], \
                        ssl_version=ssl.PROTOCOL_SSLv23)
        
        s_wrapped.sendall(content)
        log.info("Told server " + content )
    except Exception as e:
        log.info('there was an error')
        log.exception(str(e))

def run_check(script):
    # NOTE: We run check_output with shell=True so that scripts like "whatever.py" can run in
    # Windows. Otherwise we'd have to specify the interpreter, e.g. check_call(['python',
    # 'whatever.py']). Unfortunately this means that spaces in the path to the script will
    # cause things to break. The best solution would possibly be to programmatically figure out
    # what interpreter to use based on the file extension (like the shell does) and then do a
    # normal check_output without shell=True.
    scriptfile = join(settings["Checks_Dir"], script[0])
    args = script[1:]
    log.info("running {}".format(repr(' '.join([scriptfile] + args))))
    try:
        return check_output(' '.join([scriptfile] + args), shell=True)
    except CalledProcessError as e:
        log.info("Couldn't run check {}: {}".format(basename(scriptfile), e))
        return "Okay"

def getStatus():
    if DEBUG and isfile('/tmp/oldstatus'):
        return "rgsender3"

    # ugly hack for windows. make sure we're in the right directory.
    olddir = os.getcwd()
    os.chdir(application_path)
    problems = [result for result in [run_check(script).strip()
                                      for script in settings["Check_Scripts"]]
                       if result != "Okay"]
    os.chdir(olddir)
    return ",".join(problems) if problems else "Okay"

class CommandHandler(LineOnlyReceiver):
    """Recognized commands:
    restart_rgsender
    reboot
    """
    def lineReceived(self, line):
        command = line.strip()
        log.info("received command: " + command)
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

def readConfigFile(config):
    if isfile(config):
        with open(config, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                try:
                    key, val = [word.strip() for word in line.split(':', 1)]
                except ValueError:
                    log.info("Warning: unrecognized setting: " + line)
                    continue
                if key not in settings:
                    log.info("Warning: unrecognized setting: " + line)
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
    
    settings["Check_Scripts"] = [line.split(',') for line in settings["Check_Scripts"].split()]

def start(config=default_config):
    if os.name == 'nt':
        handler = logging.FileHandler(join(os.getenv('APPDATA'), 'cabsagent.log'))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        log.addHandler(handler)
        log.info('testing filehandler')

    log.info("starting up")
    log.info("CWD is {}".format(os.getcwd()))
    readConfigFile(config)
    t = Thread(target=heartbeat_loop)
    t.daemon = True
    t.start()

    if settings.get("Agent_Priv_Key") is None:
        endpoint = endpoints.TCP4ServerEndpoint(reactor, int(settings.get("Command_Port")))
        endpoint.listen(Factory.forProtocol(CommandHandler))
    else:
        start_ssl_cmd_server()
    log.info("running the reactor")
    reactor.run()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-f', '--config', default=default_config)
    argv = parser.parse_args()
    DEBUG = argv.debug
    start(argv.config)
