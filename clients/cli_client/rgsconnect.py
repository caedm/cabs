#!/usr/bin/python3
import subprocess
import sys
import time
import os
from time import sleep
from os.path import dirname, abspath
from shared.clientlib import Clientlib
from argparse import ArgumentParser
encoding = 'utf-8'

if getattr(sys, 'frozen', False):
    __file__ = sys.executable
settings = {}

try:
    import psutil
    settings["psutil"] = 'True'
except:
    settings["psutil"] = 'False'

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
    clientlib = Clientlib(os.path.dirname(os.path.abspath(__file__)), settings)


    if clientlib.readConfigFile('CABS_client.conf'):
        print("Connecting to RGS Connect...")
        cl_user = input("CAEDM User Name: ")
        cl_pass = getpass.getpass()
        #pools=getPools(cl_user,cl_pass,settings["Host_Addr"],18181)
        pools=clientlib.getPools(cl_user,cl_pass,settings["Host_Addr"], int(settings["Client_Port"]))
        pools_array = []
        for pool in pools:
            pools_array.append(pool)
        print("")
        print("Choose a pool to connect to:")
        pools_array.sort()
        for i in range(len(pools_array)):
            print(str(i) + ": " + pools_array[i][0] + ": " + pools_array[i][1])
        print("")
        cl_pool = int(input("Please enter a pool number: "))
        cl_machine = clientlib.getMachine(settings, cl_user, cl_pass, pools_array[cl_pool][0], settings["Host_Addr"], int(settings["Client_Port"]))
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
        #cl_resolution = int(input("Please choose a screen resolution: "))
        #it seems to be ignoring the resolution anyways, so we won't bother asking.
        cl_resolution = 1
        rgscommand = [settings["RGS_Location"], '-nosplash', '-Rgreceiver.Session.0.IsConnectOnStartup=1', '-Rgreceiver.Session.0.Hostname=' + cl_machine + '.et.byu.edu', '-Rgreceiver.Session.0.Username=' + cl_user, '-Rgreceiver.Session.0.Password=' + cl_pass, '-Rgreceiver.Session.0.PasswordFormat=Clear', '-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionWidth=' + str(resolutions[cl_resolution][1]), '-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionHeight=' + str(resolutions[cl_resolution][2]), '-Rgreceiver.ImageCodec.Quality=75', '-Rgreceiver.IsBordersEnabled=1', '-Rgreceiver.IsSnapEnabled=0', '-Rgreceiver.Audio.IsEnabled=1', '-Rgreceiver.Audio.IsInStereo=1', '-Rgreceiver.Audio.Quality=2', '-Rgreceiver.Mic.IsEnabled=1', '-Rgreceiver.Hotkeys.IsKeyRepeatEnabled=0', '-Rgreceiver.Clipboard.IsEnabled=1', '-Rgreceiver.Usb.IsEnabled=1', '-Rgreceiver.Network.Timeout.Dialog=60000', '-Rgsender.IsReconnectOnConsoleDisconnectEnabled=0']
        if clientlib.check_file(settings["RGS_Location"]):
            p = subprocess.Popen(rgscommand)
            watchProcess(p.pid)
        else:
            print("Error: Couldn't start connection. Nothing installed at ", settings["RGS_Location"])
    else:
        print("Could not load settings file")
