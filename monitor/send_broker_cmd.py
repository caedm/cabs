#!/usr/bin/python2
"""USAGE: ./cmd_dummy.py <command>

Recognized commands:
    query [verbose]
    tell_agent (restart|reboot) <hostname>
    autoit (enable|disable) <hostname>

Examples:
    ./cmd_dummy.py tell_agent restart rgsl-20
    ./cmd_dummy.py autoit disable rgsl-21

Query response format:
    pool,machine,status,has users,deactivated,reason

After receiving an autoit disable command, the broker will set the deactivation
reason to "autoit". The broker will not execute an autoit enable command if
the deactivation reason is set to something else, like "commandeered by
goblins"."""
import socket, ssl
from sys import argv, exit, stdout
from send_broker_cmd_settings import *

if argv[1] in ("--help", "-h"):
    print __doc__
    exit(0)

wait_response = False
if argv[1] == 'query':
    wait_response = True
command = ":".join(argv[1:]) + "\r\n"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s_wrapped = ssl.wrap_socket(s,  certfile=COMMAND_CERT,
        cert_reqs=ssl.CERT_REQUIRED, ca_certs=BROKER_CERT,
        ssl_version=ssl.PROTOCOL_SSLv23)
s_wrapped.sendall(command)

if wait_response:
    response = s_wrapped.recv(1024)
    while response:
        response = s_wrapped.recv(1024)
        stdout.write(response)
    stdout.write("\n")
