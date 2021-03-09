import subprocess
import os
import socket, ssl
from os.path import isfile
from ast import literal_eval
import json
from .client_request import *
from .broker_response import *
from collections import namedtuple
from json import JSONEncoder
from time import sleep
import json


class ServerError(Exception):
    pass


class Reconnect:
    Do = 'reconnect'
    NotSpecified = 'no preference'
    Dont = 'no-reconect'


class Clientlib:
    def __init__(self, base_file_path, settings):
        self.base_file_path = base_file_path
        self.settings = settings
        self.protocol_version = 1.0

    def getRGSversion(self):
        try:
            p = subprocess.Popen([self.settings.get("RGS_Location"), "-version"], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            out, er = p.communicate()
            version = (out + er).split()[(out + er).split().index('Version') + 1]
            return version
        except:
            return None

    def readConfigFile(self, config_file_name):
        filelocation = self.base_file_path + '/' + config_file_name
        # filelocation = os.path.dirname(os.path.abspath(application_path)) + '/LabConnect.conf'
        if not isfile(filelocation):
            return False

        with open(filelocation, 'r') as f:
            for line in f:
                line = line.strip()
                if (not line.startswith('#')) and line:
                    try:
                        (key, val) = line.split(':\t', 1)
                    except:
                        try:
                            (key, val) = line.split(None, 1)
                            key = key[:-1]
                        except:
                            key = line
                            key = key.strip()
                            key = key[:-1]
                            val = ''
                    self.settings[key] = val
            f.close()

        # insert default settings for all not specified
        if not self.settings.get("Host_Addr"):
            self.settings["Host_Addr"] = 'localhost'
        if not self.settings.get("Client_Port"):
            self.settings["Client_Port"] = 18181
        if not self.settings.get("SSL_Cert"):
            self.settings["SSL_Cert"] = None
        if not self.settings.get("Command"):
            if self.settings.get("Command-Win"):
                self.settings["Command"] = self.settings.get("Command-Win")
            elif self.settings.get("Command-Lin"):
                self.settings["Command"] = self.settings.get("Command-Lin")
            else:
                self.settings["Command"] = None
        if not self.settings.get("RGS_Options"):
            self.settings["RGS_Options"] = False
        if not self.settings.get("RGS_Location"):
            self.settings["RGS_Location"] = None
        if (not self.settings.get("Net_Domain")) or (self.settings.get("Net_Domain") == 'None'):
            self.settings["Net_Domain"] = ""
        if not self.settings.get("RGS_Version"):
            self.settings["RGS_Version"] = 'False'
        if not self.settings.get("RGS_Hide"):
            self.settings["RGS_Hide"] = 'True'

        return True

    def getPools(self, user, password, host, port, retry=0):
        # add the version check into the pool request. 
        # if self.settings.get("RGS_Version") == True:
        #     content = json.dumps(['prv', user, password, getRGSversion()]) + '\r\n'
        # else:
        #     content = json.dumps(['pr', user, password]) + '\r\n'
        # read message and save connection socket

        # build request obj here
        poolRequest = PoolReq(self.settings.get("client_version"), self.settings.get("client_name"),
                              self.getRGSversion())
        clientReq = ClientReq(poolRequest, RequestTypes.pr, user, password)

        s_wrapped = self.send_message(Clientlib.msgtostr(clientReq) + '\r\n', host, port)
        response = self.read_response(s_wrapped, retry, lambda: self.getPools(user, password, host, port, retry + 1))

        poolresponse = json.loads(response, object_hook=Clientlib.decode)
        poolsliterals = poolresponse.content.pools_string.split('\n')
        poolset = set()
        for literal in poolsliterals:
            if literal:
                poolset.add(literal_eval(literal))

        return (poolresponse.version_err_msg, poolset)

    def getMachine(self, user, password, pool, host, port, retry=0, reconnect_preference=Reconnect.NotSpecified):
        if pool == '' or pool is None:
            return ''
        machineReq = MachineReq(self.protocol_version, reconnect_preference, pool)
        clientReq = ClientReq(machineReq, RequestTypes.mr, user, password)

        s_wrapped = self.send_message(Clientlib.msgtostr(clientReq) + '\r\n', host, port)
        response = self.read_response(s_wrapped, retry, lambda: self.getMachine(user, password, pool, host, retry + 1))
        # what should the response be? return the machine and also a flag if you have an existing machine.
        # No preference ->
        # either return the machine or the choice
        try:
            response = json.loads(response, object_hook=Clientlib.decode)
            return (response.content.existing_conn, response.content.machine)
        except Exception as e:
            print(e)

    def send_message(self, message, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect((host, port))
        if (self.settings.get("SSL_Cert") is None) or (self.settings.get("SSL_Cert") == 'None'):
            s_wrapped = s
        else:
            ssl_cert = self.base_file_path + "/" + self.settings.get("SSL_Cert")
            s_wrapped = ssl.wrap_socket(s, cert_reqs=ssl.CERT_REQUIRED, ca_certs=ssl_cert,
                                        ssl_version=ssl.PROTOCOL_SSLv23)

        s_wrapped.sendall(message.encode())
        return s_wrapped

    def read_response(self, sock, retry, callback):
        response = ""
        while True:
            chunk = sock.recv(1024).decode()
            response += chunk
            if chunk == '':
                break
        # parse out my broker response
        response = json.loads(response, object_hook=Clientlib.decode)
        if response.response_type == ResponseTypes.error:
            if response.content == "Err:RETRY" and retry < 6:
                sleep(retry)
                return callback()
            else:
                raise ServerError(response.content)
        return response

    def check_file(self, path_to_file):
        return os.path.isfile(path_to_file)

    @staticmethod
    def decode(dict):
        return namedtuple('_', dict.keys())(*dict.values())

    @staticmethod
    def msgtostr(msg):
        return json.dumps(msg, indent=4, cls=MsgEncoder)


class MsgEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
