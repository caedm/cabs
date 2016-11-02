#!/usr/bin/python2
from __future__ import print_function
from argparse import ArgumentParser
import code
import socket
from subprocess import check_call, check_output
from time import time, sleep
import re
import json
from threading import Thread
import sys

machines = [pool + str(i)
            for pool in ('main', 'secondary', 'other')
            for i in range(1, 4)]
states = ['nopanel']

verbose = False

def test():
    # setup
    print('starting containers...')
    for machine in machines:
        start(machine)
    wait(lambda: all(m['status'] == "Okay" for m in dump().values()))
    print('running tests')
    global verbose
    verbose = True
    
    # test no panel status on agent
    print("\nTEST NO PANEL STATE")
    state('main1', 'set', 'nopanel')
    logon('main1', 'harry')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'no panel'
    print("main1 status is 'no panel'")

    logoff('main1')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'no panel'
    print("main1 status is 'no panel'")

    logon('main2', 'foo')
    logon('main3', 'bar')
    wait_heartbeat('main2', 'main3')
    m = request('baz', 'main')
    assert m.startswith('secondary')

    logon('main1', 'steve')
    state('main1', 'unset', 'nopanel')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'Okay'
    print("main1 status is 'Okay'")
    print("PASS")

    verbose = False
    logoff('main1')
    logoff('main2')
    logoff('main3')
    logon(m)
    wait_heartbeat(m)
    logoff(m)
    wait_heartbeat(m)
    verbose = True

    # test logic for restoring machines
    #print("requesting two machines")
    #first = request('fred', 'main')
    #second = request('fred', 'main')
    #assert first != second

    #print("logging in and requesting another machine")
    #logon(first, 'fred')
    #wait(lambda: dump()[first]['confirmed'])
    #second = request('fred', 'main')
    #assert first == second

    print("All tests pass.")

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
    machine = broker_cmd("mr", user, "mypassword", pool)
    if verbose:
        print("requested machine from {} for {}. Got {}.".format(pool, user, machine))
    return machine

def exists(container):
    return bool(check_output('docker ps -aqf name={}'.format(container).split()))

def running(container):
    return bool(check_output('docker ps -qf name={}'.format(container).split()))

def start(hostname=None, user=None):
    if not running(hostname):
        if exists(hostname):
            check_call(['docker', 'start', hostname])
        else:
            check_call('docker run -v $PWD/agent:/code --network=cabsnet --net-alias {hostname} '
                       '--hostname {hostname} --name {hostname} -d cabsagent'
                       .format(hostname=hostname), shell=True)

    # reset state
    state(hostname, 'unset', 'nopanel')
    if dump()[hostname]['status'] != 'Okay':
        logon(hostname, 'user1')
        wait_heartbeat(hostname)
        logoff(hostname)

    if user:
        logon(hostname, user)
    else:
        logoff(hostname)

def stop(hostname=None):
    m_list = [hostname] if hostname else machines

    threads = []
    for m in m_list:
        t = Thread(target=lambda: check_call(['docker', 'stop', m]))
        t.start()
        threads.append(t)
    [t.join() for t in threads]

def logon(hostname=None, user=None):
    if verbose:
        print("logging {} on to {}.".format(user, hostname))
    check_call(['docker', 'exec', '--', hostname, 'bash', '-c',
                'echo {} > /tmp/users.txt'.format(user)])

def logoff(hostname=None):
    if verbose:
        print("logging off of {}.".format(hostname))
    check_call(['docker', 'exec', '--', hostname, 'bash', '-c',
                'echo > /tmp/users.txt'])

def query():
    return broker_cmd("query", "verbose", port=18183)

def dump():
    return json.loads(broker_cmd("dump", port=18183))

def wait_heartbeat(*hosts):
    beats = {host: dump()[host]['last_heartbeat'] for host in hosts}

    def check():
        d = dump()
        return all(d[host]['last_heartbeat'] != beats[host] for host in hosts)

    wait(check)

def wait(func):
    end_time = time() + 15
    while time() < end_time:
        sleep(1)
        if func():
            return
    raise AssertionError("Timed out while waiting for condition")

def remove(hostname):
    if running(hostname):
        check_call(['docker', 'stop', hostname])
    if exists(hostname):
        check_call(['docker', 'rm', hostname])

def build():
    check_call('docker build -t cabsagent ./agent'.split())
    print("removing old containers...")

    threads = []
    for m in machines:
        t = Thread(target=remove, args=(m,))
        t.start()
        threads.append(t)
    [t.join() for t in threads]

def state(hostname=None, action=None, state=None):
    if verbose:
        print("{}ting state {} on {}.".format(action, state, hostname))
    if state == 'nopanel':
        if action == 'set':
            check_call('docker exec {} touch /tmp/nopanel'.format(hostname).split())
        if action == 'unset':
            check_call('docker exec {} rm -f /tmp/nopanel'.format(hostname).split())

def restart(hostname=None, hard=None):
    m_list = [hostname] if hostname else machines

    def stopstart(m):
        if hard:
            remove(m)
        else:
            if not running(m):
                return
            stop(m)
        start(m)

    threads = []
    for m in m_list:
        t = Thread(target=stopstart, args=(m,))
        t.start()
        threads.append(t)
    [t.join() for t in threads]

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
p.add_argument("hostname", nargs='?')
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

p = sub.add_parser("build", help="build the agent docker image")
p.set_defaults(func=build)

p = sub.add_parser("restart", help="restart the cabs agent on a machine")
p.add_argument("hostname", nargs='?')
p.add_argument("--hard", "-f", action='store_true', help="remove the container")
p.set_defaults(func=restart)

p = sub.add_parser("state", help="set the state of an agent")
p.add_argument("hostname")
p.add_argument("action", choices=['set', 'unset'])
p.add_argument("state", choices=states)
p.set_defaults(func=state)

args = vars(parser.parse_args())
func = args['func']
args.pop('func')
response = func(**args)
if response:
    if any(isinstance(response, t) for t in (dict, list)):
        print(json.dumps(response, indent=2))
    else:
        print(response)
