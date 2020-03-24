#!/usr/bin/python2
import socket, ssl
import subprocess
import sys
import time
import os
from time import sleep
from os.path import isfile
from ast import literal_eval
from os.path import dirname, join, abspath

#import wx
import json
from argparse import ArgumentParser

if getattr(sys, 'frozen', False):
    __file__ = sys.executable
root = dirname(abspath(__file__))

try:
    with open(join(root, 'version.txt'), 'r') as f:
        version=f.read().strip()
except IOError:
    version=""

settings = {}
try:
    import psutil
    settings["psutil"] = 'True'
except:
    settings["psutil"] = 'False'

command_settings = []

def getRGSversion():
    p = subprocess.Popen([settings.get("RGS_Location"), "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, er = p.communicate()
    version = (out+er).split()[(out+er).split().index('Version')+1]
    return version

def readConfigFile():
    global settings
    if getattr(sys, 'frozen', False):
        application_path = sys.executable
    else:
        application_path = __file__
    filelocation = os.path.dirname(os.path.abspath(application_path)) + '/CABS_client.conf'
    if not isfile(filelocation):
        return False

    with open(filelocation, 'r') as f:
        for line in f:
            line = line.strip()
            if (not line.startswith('#')) and line:
                try:
                    (key,val) = line.split(':\t',1)
                except:
                    #print "Warning : Check .conf syntax"
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
    if not settings.get("Client_Port"):
        settings["Client_Port"] = 18181
    if not settings.get("SSL_Cert"):
        settings["SSL_Cert"] = None
    if not settings.get("Command"):
        if settings.get("Command-Win"):
            settings["Command"] = settings.get("Command-Win")
        elif settings.get("Command-Lin"):
            settings["Command"] = settings.get("Command-Lin")
        else:
            settings["Command"] = None
    if not settings.get("RGS_Options"):
        settings["RGS_Options"] = False
    if not settings.get("RGS_Location"):
        settings["RGS_Location"] = None
    if (not settings.get("Net_Domain")) or (settings.get("Net_Domain")=='None'):
        settings["Net_Domain"] = ""
    if not settings.get("RGS_Version"):
        settings["RGS_Version"] = 'False'
    if not settings.get("RGS_Hide"):
        settings["RGS_Hide"] = 'True'

    return True

def getPools(user, password, host, port, retry=0):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    if settings.get("RGS_Version") == True:
        content = json.dumps(['prv', user, password, getRGSversion()]) + '\r\n'
    else:
        content = json.dumps(['pr', user, password]) + '\r\n'

    if (settings.get("SSL_Cert") is None) or (settings.get("SSL_Cert") == 'None'):
        s_wrapped = s
    else:
        ssl_cert = os.path.dirname(os.path.abspath(__file__)) + "/" + settings.get("SSL_Cert")
        s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=ssl_cert, ssl_version=ssl.PROTOCOL_SSLv23)

    s_wrapped.sendall(content)
    pools = ""
    while True:
        chunk = s_wrapped.recv(1024)
        pools += chunk
        if chunk == '':
            break;
    if pools.startswith("Err:"):
        if (pools == "Err:RETRY") and (retry < 6):
            sleep(retry)
            return getPools(user, password, host, port, retry+1)
        else:
            raise ServerError(pools)
    poolsliterals = pools.split('\n')
    poolset = set()
    for literal in poolsliterals:
        if literal:
            poolset.add(literal_eval(literal))
    return poolset

def getMachine(user, password, pool, host, port, retry=0):
    if pool == '' or pool is None:
        return ''
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    content = json.dumps(['mr', user, password, pool]) + '\r\n'
    if (settings.get("SSL_Cert") is None) or (settings.get("SSL_Cert") == 'None'):
        s_wrapped = s
    else:
        ssl_cert = os.path.dirname(os.path.abspath(__file__)) + "/" + settings.get("SSL_Cert")
        s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=ssl_cert, ssl_version=ssl.PROTOCOL_SSLv23)

    s_wrapped.sendall(content)
    machine = ""
    while True:
        chunk = s_wrapped.recv(1024)
        machine += chunk
        if chunk == '':
            break;
    if machine.startswith("Err:"):
        if (machine == "Err:RETRY") and (retry < 6):
            sleep(retry)
            return getMachine(user, password, pool, host, port, retry+1)
        else:
            raise ServerError(machine)
    return machine

def handleSettings(self, e):
        if e.GetId() == ID_SUBMIT_BUTTON:
            #do a Pool Request
            server = ""
            port = 0
            if settings.get("RGS_Options") == 'True':
                server = self.tab6.domandserv.server.GetValue()
                port = self.tab6.domandserv.port.GetValue()
            else:
                server = self.notebook.server.GetValue()
                port = self.notebook.port.GetValue()

            try:
                pools = getPools(username, password, server, port)
                self.poolDialog(pools, username, password, server, port)
            except ServerError as e:
                message = showError(e[0])
                print('Error')

class ServerError(Exception):
    pass

def showError(errortext):
    #generic errors
    if errortext == "pools":
        message = "The server could not be reached, or there are no availible pools, try again."
    elif errortext == "machines":
        message = "The server could not be reached, try again."
    elif errortext.startswith("Err:"):
        message = errortext.split(':',1)[1]
    else:
        message = "Unexpected Error."
    message = "CABS Error:\n" + message
    return message


    def runCommand(self, username, password, machine, port):
        if settings.get("RGS_Options") == 'True':
            #check if it is a valid file
            if argv.debug or (settings["RGS_Location"] not in (None, "None") and
                              isfile(settings["RGS_Location"])):
                if str(machine).endswith(self.tab6.domandserv.domain.GetValue().strip()):
                    address = str(machine)
                else:
                    string2add = (self.tab6.domandserv.domain.GetValue().strip())
                    if not string2add.startswith('.'):
                        string2add = '.' + string2add
                    address = str(machine) + string2add
                #process RGS settings, and build request
                command = []
                command.append(settings.get("RGS_Location"))
                command.append("-nosplash")
                command.append("-Rgreceiver.IsDisconnectWarningEnabled=1")
                command.append("-Rgreceiver.Session.0.IsConnectOnStartup=1")
                command.append("-Rgreceiver.Session.0.Hostname="+address)
                command.append("-Rgreceiver.Session.0.Username="+username)
                if sys.platform.startswith("linux"):
                    #linux can't send XOR passwords, so in it's call trace, the password will be plaintext
                    #this is only on the local machine though, the network packets are encrypted
                    command.append("-Rgreceiver.Session.0.Password="+password)
                    command.append("-Rgreceiver.Session.0.PasswordFormat=Clear")
                elif sys.platform.startswith("win"):
                    #find XOR windows password
                    XORpass = ""
                    for i in range(len(password)):
                        XORpass += hex(ord(password[i])^129)[2:]
                    command.append("-Rgreceiver.Session.0.Password="+XORpass)
                    command.append("-Rgreceiver.Session.0.PasswordFormat=XOR")

                command.extend(self.tab1.rgsSettings())
                command.extend(self.tab2.rgsSettings())
                command.extend(self.tab3.rgsSettings())
                command.extend(self.tab4.rgsSettings())
                command.extend(self.tab5.rgsSettings())
                command.extend(self.tab6.rgsSettings())
                #print "running" + str(command)

                #set command, then quit the wxapp
                global rgscommand
                rgscommand = command
                self.Destroy()
                #p = subprocess.Popen(command)
                #watchProcess(p.pid)
            else:
                #invalid RGS Location   
                dlg = wx.MessageDialog(self, "Invalid rgreceiver location\nCheck CABS_client.conf", 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
        else:
            #run the command given (non-RGS)
            if settings.get("Command") and settings.get("Command") != None and settings.get("Command") != 'None':
                if str(machine).endswith(self.notebook.domain.GetValue().strip()):
                    address = str(machine)
                else:
                    address = str(machine) + "." + (self.notebook.domain.GetValue().strip())

                command = settings.get("Command").format(user=username, address=address, password=password, port=port)
                p = subprocess.Popen(command, shell=True)
                #print "running " + command


def watchProcess(pid):
    #we need psutil for this
    if settings.get("psutil") == 'False' or settings.get("RGS_Hide") == 'False':
        sys.exit()
    #given this process we need to kill the RGS initial screen thing when it's child fork dies
    #then we exit
    try:
        process = psutil.Process(pid)
        if process.parent():
            process = process.parent()
        time.sleep(15) #wait 15 seconds, to make sure the connections start
        while(True):
            #check for the number of children's connections in the group to go down
            time.sleep(2)
            connections = []
            for child in process.children(recursive=True):
                connections.extend( child.connections(kind="tcp") )
            numout = 0
            for connection in connections:
                #if no connections are in state established (or just one connection on windows), we are done, so kill it.
                if connection.status == 'ESTABLISHED':
                    numout += 1
            if numout < 1:
                break

        #kill the processes, and ourselves too
        for child in process.children(recursive=True):
            child.kill()
        os.killpg(process.pid, 1)#this will kill our process

        sys.exit()
        #bye!
    except:
        pass


if __name__ == "__main__":
    #getpass used for cmdline passwords in text version 
    import getpass
    global argv
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    argv = parser.parse_args()


    if readConfigFile():
        print("Connecting to RGS Connect...")
        cl_user = raw_input("CAEDM User Name: ")
        cl_pass = getpass.getpass()
        #pools=getPools(cl_user,cl_pass,settings["Host_Addr"],18181)
        pools=getPools(cl_user,cl_pass,settings["Host_Addr"], int(settings["Client_Port"]))
        pools_array = []
        for pool in pools:
            pools_array.append(pool)
        print("")
        print("Choose a pool to connect to:")
        for i in range(len(pools_array)):
            print(str(i) + ": " + pools_array[i][0] + ": " + pools_array[i][1])
        print("")
        cl_pool = int(raw_input("Please enter a pool number: "))
        cl_machine = getMachine(cl_user, cl_pass, pools_array[cl_pool][0], settings["Host_Addr"], int(settings["Client_Port"]))
        print("Reservation established for " + cl_machine)
        resolutions = []
        resolutions.append(("720p",1280,720))
        resolutions.append(("1080p",1920,1080))
        resolutions.append(("1440p",2560,1440))
        resolutions.append(("4k",3640,2160))
        #print("Choose a screen resolution:")
        #for i in range(len(resolutions)):
        #    print(str(i) + ": " + resolutions[i][0])
        #print("")
        #cl_resolution = int(raw_input("Please choose a screen resolution: "))
        #it seems to be ignoring the resolution anyways, so we won't bother asking.
        cl_resolution = 1
        rgscommand = [settings["RGS_Location"], '-nosplash', '-Rgreceiver.Session.0.IsConnectOnStartup=1', '-Rgreceiver.Session.0.Hostname=' + cl_machine + '.et.byu.edu', '-Rgreceiver.Session.0.Username=' + cl_user, '-Rgreceiver.Session.0.Password=' + cl_pass, '-Rgreceiver.Session.0.PasswordFormat=Clear', '-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionWidth=' + str(resolutions[cl_resolution][1]), '-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionHeight=' + str(resolutions[cl_resolution][2]), '-Rgreceiver.ImageCodec.Quality=75', '-Rgreceiver.IsBordersEnabled=1', '-Rgreceiver.IsSnapEnabled=0', '-Rgreceiver.Audio.IsEnabled=1', '-Rgreceiver.Audio.IsInStereo=1', '-Rgreceiver.Audio.Quality=2', '-Rgreceiver.Mic.IsEnabled=1', '-Rgreceiver.Hotkeys.IsKeyRepeatEnabled=0', '-Rgreceiver.Clipboard.IsEnabled=1', '-Rgreceiver.Usb.IsEnabled=1', '-Rgreceiver.Network.Timeout.Dialog=60000', '-Rgsender.IsReconnectOnConsoleDisconnectEnabled=0']
        p = subprocess.Popen(rgscommand)
        watchProcess(p.pid)
    else:
        print("Could not load settings file")
