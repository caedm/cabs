#!/usr/bin/python2
from argparse import ArgumentParser
import code
import socket
from subprocess import check_call, check_output
from time import time, sleep
import re

def broker_cmd(*args, **kwargs):
    port = kwargs.get('port', 18181)

    # send command
    command = ":".join(args) + "\r\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("localhost", port))
    s.sendall(command)

    # get response
    response = ""
    buf = s.recv(1024)
    while buf:
        response += buf
        buf = s.recv(1024)

    s.close()
    return response

def request(user=None, pool=None):
    return broker_cmd("mr", user, "mypassword", pool)

def start(hostname=None, user=None):
    if hostname in check_output(['docker', 'ps']):
        return

    check_call('docker run --network=cabsnet --net-alias {hostname} '
               '--hostname {hostname} --name {hostname} -d cabsagent'
               .format(hostname=hostname).split())
    if user:
        logon(hostname, user)

def stop(hostname=None):
    check_call(['docker', 'kill', hostname])
    check_call(['docker', 'rm', hostname])

def logon(hostname=None, user=None):
    check_call(['docker', 'exec', '--', hostname, 'bash', '-c',
               'echo {} > /tmp/users.txt'.format(user)])

def logoff(hostname=None):
    check_call(['docker', 'exec', '--', hostname, 'bash', '-c',
               'echo > /tmp/users.txt'])

def query():
    return broker_cmd("query", "verbose", port=18183)

def dump():
    return broker_cmd("dump", port=18183)

def test():
    # setup
    print('removing existing containers...')
    ps_output = check_output(['docker', 'ps', '-a'])
    containers = [line.split()[-1] for line in ps_output.split('\n')
                                   if "cabsagent" in line and
                                   'Exited' in line]
    for c in containers:
        check_call(['docker', 'rm', c])
    print('starting containers...')
    for machine in [pool + str(i)
                    for pool in ('main', 'secondary', 'other')
                    for i in range(1, 4)]:
        start(machine)
        logoff(machine)
    wait(lambda: ',,' not in query())

    print("requesting two machines")
    first = request('fred', 'main')
    second = request('fred', 'main')
    print(dump())
    assert first != second

    print("logging in and requesting another machine")
    logon(first, 'fred')
    wait(lambda: has_users(first))
    second = request('fred', 'main')
    print(dump())
    assert first == second

def has_users(hostname):
    fields = re.search(r'(.*{}.*)'.format(hostname), query()).groups()[0].split(',')
    return fields[3] == '1'

def wait(func):
    end_time = time() + 10
    while time() < end_time:
        sleep(1)
        if func():
            return
    raise AssertionError("Timed out while waiting for condition")


parser = ArgumentParser()
sub = parser.add_subparsers()

p = sub.add_parser("request", help="request a machine")
p.add_argument("user")
p.add_argument("pool")
p.set_defaults(func=request)

p = sub.add_parser("start", help="start a machine")
p.add_argument("hostname")
p.add_argument("user", nargs='?')
p.set_defaults(func=start)

p = sub.add_parser("stop", help="stop a machine")
p.add_argument("hostname")
p.set_defaults(func=stop)

p = sub.add_parser("logon", help="log a user on to a machine")
p.add_argument("hostname")
p.add_argument("user")
p.set_defaults(func=logon)

p = sub.add_parser("logoff", help="log a user off a machine")
p.add_argument("hostname")
p.set_defaults(func=logoff)

p = sub.add_parser("query", help="print current machine info")
p.set_defaults(func=query)

p = sub.add_parser("dump", help="print current machine info")
p.set_defaults(func=dump)

p = sub.add_parser("test", help="test the broker")
p.set_defaults(func=test)

args = vars(parser.parse_args())
func = args['func']
args.pop('func')
response = func(**args)
if response:
    print response
