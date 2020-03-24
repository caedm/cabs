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

import wx
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

ID_POOL_BUTTON = wx.NewId()
ID_SAVE_BUTTON = wx.NewId()
ID_RESET_BUTTON = wx.NewId()
ID_SUBMIT_BUTTON = wx.NewId()

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


class MainPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()
        self.username.SetFocus()
    
    def InitUI(self):
        self.user_label = wx.StaticText(self, wx.ID_ANY, "Username : ", size=(80,-1))
        self.pass_label = wx.StaticText(self, wx.ID_ANY, "Password : ", size=(80,-1))
        self.username = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, size=(120,30))
        self.password = wx.TextCtrl(self, style=wx.TE_PASSWORD | wx.TE_PROCESS_ENTER, size = (120,30))
        
        self.user_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.user_sizer.Add(self.user_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 15)
        self.user_sizer.Add(self.username, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, 15)
        
        self.pass_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.pass_sizer.Add(self.pass_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 15)
        self.pass_sizer.Add(self.password, 1, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, 15)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.user_sizer, 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 6)
        self.sizer.Add(self.pass_sizer, 0, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER, 6)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        
        self.Bind(wx.EVT_TEXT_ENTER, self.passEnter)
    
    def passEnter(self, e):
        e.SetId(ID_SUBMIT_BUTTON)
        e.Skip()

#Settings start on RGS 7.1 manual page 92
class DisplayTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.Resolutions = [(60, 40), (320, 320), (640, 480), (800, 600), (1024, 768), (1152, 864), (1280, 768), (1280, 800), (1280, 960), (1280, 1024), (1360, 768), (1600, 1200), (1680, 1050), (1920, 1080), (1920, 1200), (1920, 1440), (2048, 1536), (2560, 1600)]
        self.getDisplayValues()
        self.InitUI()

    def InitUI(self):
        self.flexsizer = wx.FlexGridSizer(cols=2, vgap=3, hgap=3) #rows, cols, vgap, hgap
        self.flexsizer.AddGrowableCol(1,1)
        
        self.rez_label = wx.StaticText(self, wx.ID_ANY, "Screen Resolution:")
        self.rez_slider = wx.Slider(self, wx.ID_ANY, value=len(self.Resolutions) , minValue=0, maxValue=(len(self.Resolutions)-1), size=(-1,-1), style=wx.SL_HORIZONTAL)
        self.rez_choice = wx.TextCtrl(self, wx.ID_ANY, str(self.Resolutions[len(self.Resolutions)-1][0])+"x"+str(self.Resolutions[len(self.Resolutions)-1][1]), style=wx.TE_READONLY)
        self.rez_slider.Bind(wx.EVT_SCROLL, self.updateRezValue)
        self.rez_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.flexsizer.Add(self.rez_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)
        self.rez_sizer.Add(self.rez_slider, 1, wx.EXPAND)
        self.rez_sizer.Add(self.rez_choice, 0, wx.LEFT | wx.RIGHT, 6)
        self.flexsizer.Add(self.rez_sizer,1, wx.EXPAND)
        
        self.depth_label = wx.StaticText(self, wx.ID_ANY, "Color Depth:")
        self.depth_box = wx.ComboBox(self, wx.ID_ANY, "24-bit (High)", choices=["8-bit (Low)", "16-bit (Medium)", "24-bit (High)"], style=wx.CB_READONLY)
        self.flexsizer.Add(self.depth_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)
        self.flexsizer.Add(self.depth_box, 1, wx.EXPAND)
        
        self.imgqual_label = wx.StaticText(self, wx.ID_ANY, "Image Quality")
        self.imgqual_box = wx.SpinCtrl(self, wx.ID_ANY, "75", style=wx.SP_ARROW_KEYS, min=0, max=100, initial=75)
        self.flexsizer.Add(self.imgqual_label, 0 , wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)
        self.flexsizer.Add(self.imgqual_box, 1, wx.EXPAND)
        
        #self.chkbxsizer = wx.WrapSizer() #Need wxPython 2.9 or greater for this
        self.chkbxsizer = wx.GridSizer(cols=2, vgap=2, hgap=3)
        self.chkfull = wx.CheckBox(self, wx.ID_ANY, "Fullscreen")
        self.chkbxsizer.Add(self.chkfull, 0, wx.EXPAND) 
        self.chkspan = wx.CheckBox(self, wx.ID_ANY, "Enable Spanning")
        self.chkbxsizer.Add(self.chkspan, 0, wx.EXPAND)
        self.chkmatch = wx.CheckBox(self, wx.ID_ANY, "Match Client Display")
        self.chkbxsizer.Add(self.chkmatch, 0, wx.EXPAND)
        self.chkborders = wx.CheckBox(self, wx.ID_ANY, "Borders")
        self.chkbxsizer.Add(self.chkborders, 0, wx.EXPAND)
        self.chksnap = wx.CheckBox(self, wx.ID_ANY, "Snap to Edge")
        self.chkbxsizer.Add(self.chksnap, 0, wx.EXPAND)
        self.chkconbar = wx.CheckBox(self, wx.ID_ANY, "Display Connection Bar in Fullscreen")
        self.chkbxsizer.Add(self.chkconbar, 0, wx.EXPAND)
        self.chkback = wx.CheckBox(self, wx.ID_ANY, "Show Desktop Background")
        self.chkbxsizer.Add(self.chkback, 0, wx.EXPAND)
        self.chkdrag = wx.CheckBox(self, wx.ID_ANY, "Show while Dragging")
        self.chkbxsizer.Add(self.chkdrag, 0, wx.EXPAND)
        self.chkani = wx.CheckBox(self, wx.ID_ANY, "Window/Menu Animations")
        self.chkbxsizer.Add(self.chkani, 0, wx.EXPAND)
        self.chkthemes = wx.CheckBox(self, wx.ID_ANY, "Show Themes")
        self.chkbxsizer.Add(self.chkthemes, 0, wx.EXPAND)
        self.chkcache = wx.CheckBox(self, wx.ID_ANY, "Cache Bitmaps")
        self.chkbxsizer.Add(self.chkcache, 0, wx.EXPAND)
        self.chkautosize = wx.CheckBox(self, wx.ID_ANY, "Autosizing")
        self.chkbxsizer.Add(self.chkautosize, 0, wx.EXPAND)
        self.chkcomposition = wx.CheckBox(self, wx.ID_ANY, "Desktop Composition")
        self.chkbxsizer.Add(self.chkcomposition, 0, wx.EXPAND)
        self.chksmoothing = wx.CheckBox(self, wx.ID_ANY, "Font Smoothing")
        self.chkbxsizer.Add(self.chksmoothing, 0, wx.EXPAND)
        
        self.Bind(wx.EVT_CHECKBOX, self.disableStuff)
        self.disableStuff(None)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.flexsizer, 0, wx.EXPAND | wx.TOP, 6)
        self.sizer.Add(self.chkbxsizer, 0, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        

    def getDisplayValues(self):
        disp = wx.Display(0)
        self.dispCount = disp.GetCount()
        self.maxRez =  disp.GetClientArea()#max rez rectangle
        self.maxWidth = self.maxRez[2] - self.maxRez[0]
        self.maxHeight = self.maxRez[3] - self.maxRez[1]    
        self.maxRezOneScreen =  disp.GetGeometry()#max rez rectangle one screen
        self.maxWidthOneScreen = self.maxRezOneScreen[2] - self.maxRezOneScreen[0]
        self.maxHeightOneScreen = self.maxRezOneScreen[3] - self.maxRezOneScreen[1]
        Rezolutions = []
        #now remove rezolutions above that
        for rez in self.Resolutions:
            if (rez[0] < self.maxWidth) and (rez[1] < self.maxHeight):
                Rezolutions.append(rez)
        self.Resolutions = Rezolutions
    
    def updateRezValue(self, e):
        self.rez_choice.ChangeValue(str(self.Resolutions[self.rez_slider.GetValue()][0])+"x"+str(self.Resolutions[self.rez_slider.GetValue()][1]))
    
    def disableStuff(self, e):
        #disable the things that you can't touch at the right times.
        self.chkspan.Enable(self.chkfull.IsChecked())
        self.chkborders.Enable(not self.chkfull.IsChecked())
        self.chksnap.Enable(not self.chkfull.IsChecked())
        #These I don't know when to enable, so they are all disabled for now
        self.chkconbar.Disable()
        self.chkback.Disable()
        self.chkdrag.Disable()
        self.chkani.Disable()
        self.chkthemes.Disable()
        self.chkcache.Disable()
        self.chkautosize.Disable()
        self.chkcomposition.Disable()
        self.chksmoothing.Disable()
        
        self.depth_box.Disable()
        self.depth_label.Hide()
        self.depth_box.Hide()
        
        self.chkconbar.Hide()
        self.chkback.Hide()
        self.chkdrag.Hide()
        self.chkani.Hide()
        self.chkthemes.Hide()
        self.chkcache.Hide()
        self.chkautosize.Hide()
        self.chkcomposition.Hide()
        self.chksmoothing.Hide()
    
    def load(self, default):
        if(default):
            #load defaults
            self.rez_slider.SetValue(len(self.Resolutions)-1)
            self.updateRezValue(None)
            self.depth_box.SetSelection(2)
            self.imgqual_box.SetValue(75)
            self.chkfull.SetValue(False)
            self.chkspan.SetValue(False)
            self.chkmatch.SetValue(False)
            self.chkborders.SetValue(False)
            self.chksnap.SetValue(False)
            self.chkconbar.SetValue(False)
            self.chkback.SetValue(False)
            self.chkdrag.SetValue(False)
            self.chkani.SetValue(False)
            self.chkthemes.SetValue(False)
            self.chkcache.SetValue(False)
            self.chkautosize.SetValue(False)
            self.chkcomposition.SetValue(False)
            self.chksmoothing.SetValue(False)
            self.disableStuff(None)
        else:
            #load from saved settings
            pass
    
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        if self.chkfull.IsEnabled() and self.chkfull.IsChecked():
            if (self.chkspan.IsEnabled() and self.chkspan.IsChecked()) or (self.chkmatch.IsEnabled() and self.chkmatch.IsChecked()):
                #Spanning enabled
                cmdargs.append("-Rgreceiver.IsMatchReceiverResolutionEnabled=1")
                cmdargs.append("-Rgreceiver.IsMatchReceiverPhysicalDisplaysEnabled=1")
                cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionWidth="+str(self.maxWidth))
                cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionHeight="+str(self.maxHeight))
            else:
                #No spanning
                cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.IsPreferredResolutionEnabled=1")
                cmdargs.append("-Rgreceiver.Session.0.RemoteDisplayWindow.X=0")
                cmdargs.append("-Rgreceiver.Session.0.RemoteDisplayWindow.Y=0")
                cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionWidth="+str(self.maxWidthOneScreen))
                cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionHeight="+str(self.maxHeightOneScreen))
        else:   
            cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionWidth="+str(self.Resolutions[self.rez_slider.GetValue()][0]))
            cmdargs.append("-Rgreceiver.Session.0.VirtualDisplay.PreferredResolutionHeight="+str(self.Resolutions[self.rez_slider.GetValue()][1]))
        
        if self.imgqual_box.IsEnabled():
            cmdargs.append("-Rgreceiver.ImageCodec.Quality="+str(self.imgqual_box.GetValue()))
        
        if self.chkborders.IsEnabled() and self.chkborders.IsChecked():
            cmdargs.append("-Rgreceiver.IsBordersEnabled=1")
        else:
            cmdargs.append("-Rgreceiver.IsBordersEnabled=1")
        
        if self.chksnap.IsEnabled() and self.chksnap.IsChecked():   
            cmdargs.append("-Rgreceiver.IsSnapEnabled=1")
        else:
            cmdargs.append("-Rgreceiver.IsSnapEnabled=0")
        
        return cmdargs
        
class AudioTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.chkmute = wx.CheckBox(self, wx.ID_ANY, "Mute Audio")
        self.sizer.Add(self.chkmute, 0, wx.TOP, 6)
        
        self.qual_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.qual_label = wx.StaticText(self, wx.ID_ANY, "Audio Quality:")
        self.qual_choice = wx.ComboBox(self, wx.ID_ANY, "Medium", choices=["Low", "Medium", "High"], style=wx.CB_READONLY)
        self.qual_sizer.Add(self.qual_label, 0, wx.ALIGN_CENTER | wx.LEFT, 3)
        self.qual_sizer.Add(self.qual_choice, 1, wx.EXPAND)
        self.sizer.Add(self.qual_sizer, 0, wx.EXPAND)
        
        self.chkstereo = wx.CheckBox(self, wx.ID_ANY, "Stereo Sound")
        self.chkstereo.SetValue(True)
        self.sizer.Add(self.chkstereo, 0)
        
        self.chksessiononly = wx.CheckBox(self, wx.ID_ANY, "Sound for Active Session Only")
        self.sizer.Add(self.chksessiononly, 0)
        
        self.chkmic = wx.CheckBox(self, wx.ID_ANY, "Microphone")
        self.sizer.Add(self.chkmic, 0)
            
        self.Bind(wx.EVT_CHECKBOX, self.disableStuff)
        self.disableStuff(None)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

    def disableStuff(self, e):
        self.qual_label.Enable(not self.chkmute.IsChecked())
        self.qual_choice.Enable(not self.chkmute.IsChecked())
        self.chkstereo.Enable(not self.chkmute.IsChecked())
        self.chksessiononly.Enable(not self.chkmute.IsChecked())
        self.chkmic.Enable(not self.chkmute.IsChecked())
    
    def load(self, default):
        if(default):
            #load defaults
            self.chkmute.SetValue(False)
            self.qual_choice.SetSelection(1)
            self.chkstereo.SetValue(True)
            self.chksessiononly.SetValue(False)
            self.chkmic.SetValue(False)
            self.disableStuff(None)
        else:
            #load from saved settings
            pass
    
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        if self.chkmute.IsEnabled() and self.chkmute.IsChecked():
            cmdargs.append("-Rgreceiver.Audio.IsEnabled=0")
        else:
            cmdargs.append("-Rgreceiver.Audio.IsEnabled=1")
            if self.chkstereo.IsEnabled() and self.chkstereo.IsChecked():
                cmdargs.append("-Rgreceiver.Audio.IsInStereo=1")
            else:
                cmdargs.append("-Rgreceiver.Audio.IsInStereo=1")
            if self.qual_choice.IsEnabled():
                cmdargs.append("-Rgreceiver.Audio.Quality="+self.qual_choice.GetString(self.qual_choice.GetSelection()))
            if self.chksessiononly.IsEnabled() and self.chksessiononly.IsChecked():
                cmdargs.append("-Rgreceiver.Audio.IsFollowsFocusEnabled=1")
            if self.chkmic.IsEnabled():
                cmdargs.append("-Rgreceiver.Mic.IsEnabled=1")   
        return cmdargs

class KeyboardTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.wincombo_label = wx.StaticText(self, wx.ID_ANY, "Special Windows key combinations should be handled:")
        self.sizer.Add(self.wincombo_label,0, wx.ALL, 6)
        
        self.wincombo_rb0 = wx.RadioButton(self, label="On the Remote Computer", style=wx.RB_GROUP)
        self.wincombo_rb1 = wx.RadioButton(self, label="On the Local Computer")
        self.wincombo_rb2 = wx.RadioButton(self, label="On the Remote Computer in Fullscreen")
        self.wincombo_rb2.SetValue(True)
        self.sizer.Add(self.wincombo_rb0, 0, wx.LEFT, 30)
        self.sizer.Add(self.wincombo_rb1, 0, wx.LEFT, 30)
        self.sizer.Add(self.wincombo_rb2, 0, wx.LEFT, 30)
        
        self.chkrepeat = wx.CheckBox(self, wx.ID_ANY, "Enable RGS Key Repeat")
        self.sizer.Add(self.chkrepeat, 0, wx.TOP, 6)
        
        self.disableStuff(None)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
    
    def disableStuff(self, e):
        self.wincombo_rb0.Enable(False)
        self.wincombo_rb1.Enable(False)
        self.wincombo_rb2.Enable(False)
        
    def load(self, default):
        if(default):
            #load defaults
            self.wincombo_rb2.SetValue(True)
            self.chkrepeat.SetValue(False)
            self.disableStuff(None)
        else:
            #load from saved settings
            pass
    
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        if self.chkrepeat.IsEnabled():
            cmdargs.append("-Rgreceiver.Hotkeys.IsKeyRepeatEnabled="+str(int(self.chkrepeat.IsChecked())))
        if self.wincombo_rb0.IsEnabled():
            cmdargs.append("-Rgreceiver.Hotkeys.IsSendCtrlAltEndAsCtrlAltDeleteEnabled="+str(int(self.wincombo_rb0.IsChecked()))) 

        return cmdargs

class DevicesTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.label = wx.StaticText(self, wx.ID_ANY, "Make the following Devices on this machine available:")
        self.sizer.Add(self.label, 0, wx.ALL, 6)
        
        self.chkdrives = wx.CheckBox(self, wx.ID_ANY, "Disk Drives")
        self.sizer.Add(self.chkdrives, 0, wx.LEFT, 30)
        self.chkprinters = wx.CheckBox(self, wx.ID_ANY, "Printers")
        self.sizer.Add(self.chkprinters, 0, wx.LEFT, 30)
        self.chkports = wx.CheckBox(self, wx.ID_ANY, "Serial Ports")
        self.sizer.Add(self.chkports, 0, wx.LEFT, 30)
        self.chkclip = wx.CheckBox(self, wx.ID_ANY, "Clipboard")
        self.sizer.Add(self.chkclip, 0, wx.LEFT, 30)
        self.chkclip.SetValue(True)
        self.chkcards = wx.CheckBox(self, wx.ID_ANY, "Smart Cards")
        self.sizer.Add(self.chkcards, 0, wx.LEFT, 30)
        self.chkusb = wx.CheckBox(self, wx.ID_ANY, "USB Devices")
        self.sizer.Add(self.chkusb, 0, wx.LEFT, 30)
        
        self.disableStuff(None)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
    
    def disableStuff(self, e):
        self.chkdrives.Enable(False)
        self.chkprinters.Enable(False)
        self.chkports.Enable(False)
        self.chkcards.Enable(False)

    def load(self, default):
        if(default):
            #load defaults
            self.chkdrives.SetValue(False)
            self.chkprinters.SetValue(False)
            self.chkports.SetValue(False)
            self.chkclip.SetValue(True)
            self.chkcards.SetValue(False)
            self.chkusb.SetValue(False)
            self.disableStuff(None)
        else:
            #load from saved settings
            pass
    
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        if self.chkclip.IsEnabled():
            cmdargs.append("-Rgreceiver.Clipboard.IsEnabled="+str(int(self.chkclip.IsChecked())))
        if self.chkusb.IsEnabled():
            cmdargs.append("-Rgreceiver.Usb.IsEnabled="+str(int(self.chkclip.IsChecked())))

        return cmdargs

class TimersTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.def_rb = wx.RadioButton(self, label="Use Default Timeout Values", style=wx.RB_GROUP)
        self.cus_rb = wx.RadioButton(self, label="Use the Following Timeout Values (in seconds)")
        self.sizer.Add(self.def_rb, 0, wx.TOP, 6)
        self.sizer.Add(self.cus_rb, 0)
        
        self.cus_sizer = wx.FlexGridSizer(cols=2, vgap=3, hgap=3)
        self.error_label = wx.StaticText(self, wx.ID_ANY, "Error Timeout")
        self.error_box = wx.SpinCtrl(self, wx.ID_ANY, "0", style=wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        self.cus_sizer.Add(self.error_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cus_sizer.Add(self.error_box, 1, wx.EXPAND)
        
        self.warn_label = wx.StaticText(self, wx.ID_ANY, "Warning Timeout")
        self.warn_box = wx.SpinCtrl(self, wx.ID_ANY, "0", style=wx.SP_ARROW_KEYS, min=0, max=60, initial=0)
        self.cus_sizer.Add(self.warn_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cus_sizer.Add(self.warn_box, 1, wx.EXPAND)

        self.dialog_label = wx.StaticText(self, wx.ID_ANY, "Dialog Timeout")
        self.dialog_box = wx.SpinCtrl(self, wx.ID_ANY, "60", style=wx.SP_ARROW_KEYS, min=0, max=99, initial=60)
        self.cus_sizer.Add(self.dialog_label, 0, wx.ALIGN_CENTER_VERTICAL)
        self.cus_sizer.Add(self.dialog_box, 1, wx.EXPAND)
        
        self.cus_sizer.AddGrowableCol(1,1)
        self.sizer.Add(self.cus_sizer, 1, wx.EXPAND)
        
        self.Bind(wx.EVT_RADIOBUTTON, self.disableStuff)
        self.disableStuff(None)
        
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
    
    def disableStuff(self, e):
        self.error_label.Enable(self.cus_rb.GetValue())
        self.error_box.Enable(self.cus_rb.GetValue())
        self.warn_label.Enable(self.cus_rb.GetValue())
        self.warn_box.Enable(self.cus_rb.GetValue())
        self.dialog_label.Enable(self.cus_rb.GetValue())
        self.dialog_box.Enable(self.cus_rb.GetValue())

    def load(self, default):
        if(default):
            #load defaults
            self.def_rb.SetValue(True)
            self.error_box.SetValue(0)
            self.warn_box.SetValue(0)
            self.dialog_box.SetValue(60)
            self.disableStuff(None)
        else:
            #load from saved settings
            pass
    
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        
        if self.cus_rb.GetValue():
            cmdargs.append("-Rgreceiver.Network.Timeout.Error="+str(int(self.error_box.GetValue())*1000))
            cmdargs.append("-Rgreceiver.Network.Timeout.Warning="+str(int(self.warn_box.GetValue())*1000))
            cmdargs.append("-Rgreceiver.Network.Timeout.Dialog="+str(int(self.dialog_box.GetValue())*1000))
        
        else:
            cmdargs.append("-Rgreceiver.Network.Timeout.Dialog=60000")
        
        return cmdargs

class OtherTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()

    def InitUI(self):
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        #self.savebttn = wx.Button(self, ID_SAVE_BUTTON, label="Save Settings")
        #self.sizer.Add(self.savebttn, 0, wx.EXPAND)
        #
        #self.resetbttn = wx.Button(self, ID_RESET_BUTTON, label="Reset Defaults")
        #self.sizer.Add(self.resetbttn, 0, wx.EXPAND)
        #
        #self.savebttn.Bind(wx.EVT_BUTTON, self.passOn)
        #self.resetbttn.Bind(wx.EVT_BUTTON, self.passOn)
        
        self.domandserv = DomainAndServer(self)
        self.sizer.Add(self.domandserv, 0, wx.EXPAND | wx.ALL, 18)
        
        self.chkreconnect = wx.CheckBox(self, wx.ID_ANY, label="Reconnect on Lost Connection")
        self.sizer.Add(self.chkreconnect, 0)
        self.chkroles = wx.CheckBox(self, wx.ID_ANY, label="Show Public Roles")
        self.sizer.Add(self.chkroles, 0)
        self.chkroles.SetValue(True)        

        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
    
    def passOn(self, e):
        e.Skip()

    def load(self, default):
        if(default):
            self.chkreconnect.SetValue(False)
            self.chkroles.SetValue(True)
            self.domandserv.domain.ChangeValue(settings.get("Net_Domain"))
            self.domandserv.server.ChangeValue(settings.get("Host_Addr"))
            self.domandserv.port.SetValue(int(settings.get("Client_Port")))
        else:
            #load from saved settings
            pass
    def rgsSettings(self):
        #return list of string arguments for RGS
        cmdargs = []
        cmdargs.append("-Rgsender.IsReconnectOnConsoleDisconnectEnabled="+str(int(self.chkreconnect.IsChecked())))
        return cmdargs

class DomainAndServer(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.InitUI()
    def InitUI(self):
        self.domain_label = wx.StaticText(self, wx.ID_ANY, "Domain : ", size=(90,-1))
        self.server_label = wx.StaticText(self, wx.ID_ANY, "CABS Server : ", size=(90,-1))
        self.domain = wx.TextCtrl(self, value=settings.get("Net_Domain"), style=wx.TE_LEFT, size=(-1,30))
        self.server = wx.TextCtrl(self, value=settings.get("Host_Addr"), style=wx.TE_LEFT, size = (-1,30))
        self.port_label = wx.StaticText(self, wx.ID_ANY, "Port : ", size = (90,-1))
        self.port = wx.SpinCtrl(self, value=settings.get("Client_Port"), style=wx.SP_ARROW_KEYS, min=1024, max=65535, initial=int(settings.get("Client_Port")))
        
        self.sizer = wx.FlexGridSizer(cols=2, vgap=3, hgap=3)
        self.sizer.Add(self.domain_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 6)
        self.sizer.Add(self.domain, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, 6)
        
        self.sizer.Add(self.server_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 6)
        self.sizer.Add(self.server, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, 6)
        
        self.sizer.Add(self.port_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.LEFT, 6)
        self.sizer.Add(self.port, 0, wx.EXPAND | wx.ALIGN_CENTER | wx.RIGHT, 6)
        
        self.sizer.AddGrowableCol(1,1)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)

class PickPoolDialog(wx.Dialog):
    def __init__(self, parent, pools):
        wx.Dialog.__init__(self, parent)
        self.pools = pools
        self.choice = None
        self.SetMinSize(wx.Size(270, 300))
        self.InitUI()
        
    def InitUI(self):
        self.panel = wx.Panel(self)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        for pool in sorted(self.pools):
            #Only availible in wx 2.9.2 or greater
            #self.sizer.Add(wx.CommandLinkButton(self.panel, wx.ID_ANY, mainLabel=pool[0], note=pool[1]),1,wx.EXPAND)
            #labelstring = '_'*( (len(pool[1])/2) - (len(pool[0])/2) ) + pool[0] + '_'*( (len(pool[1])/2) - (len(pool[0])/2) ) + '\n\n' + pool[1]
            labelstring = pool[0] + ' : ' + pool[1]
            self.sizer.Add(wx.Button(self.panel, ID_POOL_BUTTON, label=labelstring, style=wx.BORDER_NONE), 1, wx.EXPAND | wx.ALL, 3)
        self.panel.Bind(wx.EVT_BUTTON, self.setChoice)
        self.panel.SetSizer(self.sizer)
        
        self.mainsizer = wx.BoxSizer(wx.VERTICAL)
        self.mainsizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.SetSize((-1,-1))
    
    def setChoice(self, e):
        self.choice = e.GetEventObject().GetLabel().split(' : ',1)[0]
        self.Destroy()
    
    def getChoice(self):
        return self.choice

class MainWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="RGSConnect v" + version, size=(-1,-1))
        self.CreateStatusBar()
        
        self.InitUI()
        self.CheckSettings()
        self.Center()
        self.Show()
        
        
    def InitUI(self):
        
        p = wx.Panel(self)
        headerimage = wx.Image(join(root, 'Header.png'), wx.BITMAP_TYPE_ANY)
        header = wx.StaticBitmap(p, wx.ID_ANY, wx.BitmapFromImage(headerimage))
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(header, 0, wx.BOTTOM, 0)
        self.login = MainPage(p)
        self.Bind(wx.EVT_TEXT_ENTER, self.handleSettings)
        self.sizer.Add(self.login, 0, wx.EXPAND)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)  
        self.button_submit = wx.Button(p, ID_SUBMIT_BUTTON, "Connect")
        self.button_submit.Bind(wx.EVT_BUTTON, self.handleSettings)
        self.button_sizer.Add(self.button_submit, 1, wx.EXPAND | wx.ALL, 9)
        
        if settings.get("RGS_Options") == 'True':
            #Build button
            button_settings = wx.Button(p, wx.ID_ANY, "RGS Options")
            button_settings.Bind(wx.EVT_BUTTON, self.toggleOptions)
            self.button_sizer.Add(button_settings, 1, wx.ALL, 9)
            self.sizer.Add(self.button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT , 92)
            #Build Settings tabs
            self.notebook = wx.Notebook(p)
            
            self.tab1 = DisplayTab(self.notebook)
            self.tab2 = AudioTab(self.notebook)
            self.tab3 = KeyboardTab(self.notebook)
            self.tab4 = DevicesTab(self.notebook)
            self.tab5 = TimersTab(self.notebook)
            self.tab6 = OtherTab(self.notebook)
            
            self.notebook.AddPage(self.tab1, "Display")
            self.notebook.AddPage(self.tab2, "Audio")
            self.notebook.AddPage(self.tab3, "Keyboard")
            self.notebook.AddPage(self.tab4, "Devices")
            self.notebook.AddPage(self.tab5, "Timers")
            self.notebook.AddPage(self.tab6, "Other")
                
            self.Bind(wx.EVT_BUTTON, self.handleSettings)
        else:   
            button_settings = wx.Button(p, wx.ID_ANY, "Options")
            button_settings.Bind(wx.EVT_BUTTON, self.toggleOptions)
            self.button_sizer.Add(button_settings, 1, wx.ALL, 9)
            self.sizer.Add(self.button_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 92)
            
            self.notebook = DomainAndServer(p)
        
        self.notebook.Hide()    
        self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 3)
        
        p.SetSizer(self.sizer)
        p.SetAutoLayout(1)
        self.sizer.Fit(self)
        #self.SetSize((450,-1))
        self.SetSize((-1,-1))

    def CheckSettings(self):
        if (settings.get("SSL_Cert") is not None) and (settings.get("SSL_Cert") != 'None'):
            ssl_cert = os.path.dirname(os.path.abspath(__file__)) + "/" + settings.get("SSL_Cert")
            if not isfile(ssl_cert):
                wx.MessageBox('Could not find the SSL certificate at\n{0}'.format(ssl_cert), 'Error', wx.CANCEL | wx.ICON_ERROR)
    
    def toggleOptions(self, e):
        if self.notebook.IsShown():
            self.notebook.Hide()    
            self.sizer.Fit(self)
            #self.SetSize((450,-1))
            self.SetSize((-1,-1))
        else:
            self.notebook.Show()
            self.sizer.Fit(self)
            #self.SetSize((450,-1))
            self.SetSize((-1,-1))

    def handleSettings(self, e):
        if e.GetId() == ID_SUBMIT_BUTTON:
            #do a Pool Request
            username = self.login.username.GetValue()
            password = self.login.password.GetValue()
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
                dlg = wx.MessageDialog(self, message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
            #except:
            #    message = showError("pools")
            #    dlg = wx.MessageDialog(self, message, 'Error', wx.OK | wx.ICON_ERROR)
            #    dlg.ShowModal()
        
        elif e.GetId() == ID_SAVE_BUTTON:
            #save settings, which will be loaded automatically at the start with load(false), once we get it goin
            pass
        elif e.GetId() == ID_RESET_BUTTON:
            #We reset to default settings
            self.tab1.load(True)
            self.tab2.load(True)
            self.tab3.load(True)
            self.tab4.load(True)
            self.tab5.load(True)
            self.tab6.load(True)
    
    def poolDialog(self, pools, username, password, server, port):
        if pools:
            dlg = PickPoolDialog(self, pools)
            dlg.ShowModal()
            poolchoice = dlg.getChoice()
            dlg.Destroy()
            if poolchoice is None:
                return
            try:
                machine = getMachine(username, password, poolchoice, server, port)
            except ServerError as e:
                message = showError(e[0])
                dlg = wx.MessageDialog(self, message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
            except:
                message = showError("machines")
                dlg = wx.MessageDialog(self, message, 'Error', wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
            else:
                #run the RGS command
                #print machine
                self.runCommand(username, password, machine, port)
        else:
            message = showError("machines")
            dlg = wx.MessageDialog(self, message, 'Error', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()

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

class NoConf(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="CABS", size=(-1,-1))
        self.Center()
        self.showMessage()
    
    def showMessage(self):
        filelocation = os.path.dirname(os.path.abspath(__file__)) + '/'
        wx.MessageBox('Could not find CABS_client.conf in:\n{0}'.format(filelocation), 'Error', wx.CANCEL | wx.ICON_ERROR)
        self.Destroy()

if __name__ == "__main__":
    global argv
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    argv = parser.parse_args()

    global rgscommand
    rgscommand = None

    if readConfigFile():
        app = wx.App(False)
        MainWindow(None).Show()
        app.MainLoop()
    
        if rgscommand:
            if argv.debug:
                 print rgscommand
                 sys.exit()
            p = subprocess.Popen(rgscommand)
            watchProcess(p.pid)
    else:
        app = wx.App(False)
        NoConf(None).Show()
        app.MainLoop()
