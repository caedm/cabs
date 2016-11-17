#!/usr/bin/python2
from __future__ import print_function
from argparse import ArgumentParser
import code
import socket
from subprocess import check_call, check_output, STDOUT
from time import time, sleep
import re
import json
from threading import Thread
import sys
import traceback

machines = [pool + str(i)
            for pool in ('main', 'secondary', 'other')
            for i in range(1, 4)]
states = ['no_panel', 'old_status']
verbose = False
dump_on_failure = True
dirty_configs = set()

###############################################################################
# TESTS
###############################################################################

def test_machine_timeout():
    # NOTE: we assume these are the values set in the broker config.
    broker_machine_check = 5
    broker_timeout_time = 5
    wait_time = broker_timeout_time + broker_machine_check
    
    stop('main1')
    wait(lambda: dump()['main1']['status'] == None, timeout=wait_time)
    print('main1 status is null')

    start('main1')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == "Okay"
    print('main1 status is Okay')

def test_pscheck():
    write_config('main1', 'Process_Listen', 'foobar')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'foobar not found'
    print('main1 status is "foobar not found"')

    write_config('main1', 'Process_Listen', 'python')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'Okay'
    print('main1 status is "Okay"')

def test_oldstatus():
    state('main1', 'set', 'oldstatus')
    wait_heartbeat('main1')
    status = dump()['main1']['status']
    assert status.endswith('Okay')
    print('main1 status is ' + status)

def test_nopanel():
    state('main1', 'set', 'no_panel')
    logon('main1', 'harry')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'no_panel'
    print("main1 status is 'no_panel'")

    ts = timestamp('main1')

    logoff('main1')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'no_panel'
    print("main1 status is 'no_panel'")

    assert "rebooting" in logs('main1', ts)
    print("main1 rebooted")

    logon('main2', 'foo')
    logon('main3', 'bar')
    wait_heartbeat('main2', 'main3')
    m = request('baz', 'main')
    assert m.startswith('secondary')

    logon('main1', 'steve')
    state('main1', 'unset', 'no_panel')
    wait_heartbeat('main1')
    assert dump()['main1']['status'] == 'Okay'
    print("main1 status is 'Okay'")

def test_restoring():
    first = request('fred', 'main')
    second = request('fred', 'main')
    assert first != second

    logon(first, 'fred')
    wait(lambda: dump()[first]['confirmed'])
    second = request('fred', 'main')
    assert first == second

    state(first, 'set', 'no_panel')
    wait_heartbeat(first)
    second = request('fred', 'main')
    assert first != second

def test_handle_json():
    m = request('fred', 'main', json=True)
    assert m.startswith('main')

test_funcs = [test_handle_json, test_nopanel, test_oldstatus,
              test_machine_timeout, test_pscheck, test_restoring]

###############################################################################
# UTILS
###############################################################################

def logs(hostname, since=None):
    return check_output(['docker', 'logs'] +
            ([] if not since else ['--since', since]) +
            [hostname], stderr=STDOUT)


def timestamp(hostname):
    last_line = (check_output(['docker', 'logs', '-t', hostname], stderr=STDOUT)
                 .strip().split('\n')[-1])
    return last_line if isinstance(last_line, basestring) else last_line[0]

def setup():
    clean_configs()
    [start(m) for m in machines]
    expected = {'status': "Okay", 'confirmed': False, 'user': None}
    wait(lambda: all(all(m[key] == expected[key] for key in expected)
                     for m in dump().values()))

def clean_configs():
    global dirty_configs
    for machine in dirty_configs:
         check_call('docker exec {} rm /etc/cabsagent.conf'.format(machine).split())
         restart(machine)
    dirty_configs = set()

def write_config(machine, key, value):
    global dirty_configs
    global verbose

    if verbose:
        print("setting '{}: {}' on {}".format(key, value, machine))
    check_call(['docker', 'exec', '--', machine, 'bash', '-c',
                'echo {}: {} >> /etc/cabsagent.conf'.format(key, value)])

    tmp_verbose = verbose
    verbose = False
    restart(machine)
    verbose = tmp_verbose
    dirty_configs.add(machine)

def broker_cmd(*args, **kwargs):
    port = kwargs.get('port', 18181)
    use_json = kwargs.get('json', False)

    if use_json and verbose:
        print('wrapping command in json')

    # send command
    command = (json.dumps if use_json else ":".join)(args) + "\r\n"
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

def exists(container):
    return bool(check_output('docker ps -aqf name={}'.format(container).split()))

def running(container):
    return bool(check_output('docker ps -qf name={}'.format(container).split()))

def wait_heartbeat(*hosts):
    beats = {host: dump()[host]['last_heartbeat'] for host in hosts}

    def check():
        d = dump()
        return all(d[host]['last_heartbeat'] != beats[host] for host in hosts)

    wait(check)

def wait(func, timeout=10):
    end_time = time() + timeout
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

###############################################################################
# USER COMMANDS
###############################################################################

def test():
    # setup
    global verbose

    for t in test_funcs:
        try:
            print(t.__name__.replace('_', ' ').upper())
            print('setting up...')
            setup()
            verbose = True
            t()
            verbose = False
            print("PASS\n")
        except AssertionError as e:
            if dump_on_failure:
                print(json.dumps(dump(), indent=2))
            traceback.print_exc()
            clean_configs()
            return

    print("All tests pass.")
    print("cleaning up...")
    setup()

def request(user=None, pool=None, **kwargs):
    machine = broker_cmd("mr", user, "mypassword", pool, **kwargs)
    if verbose:
        print("requested machine from {} for {}. Got {}.".format(pool, user, machine))
    return machine

def start(hostname=None, user=None):
    if 'cabsagent' not in check_output(['docker', 'images']):
        check_call('docker build -t cabsagent ./agent'.split())

    if not running(hostname):
        if exists(hostname):
            check_output(['docker', 'start', hostname])
        else:
            check_output('docker run -v $PWD/agent:/code --network=cabsnet --net-alias {hostname} '
                       '--hostname {hostname} --name {hostname} -d cabsagent'
                       .format(hostname=hostname), shell=True)

    # reset state
    info = dump()[hostname]
    if info['status'] is None:
        wait_heartbeat(hostname)
        info = dump()[hostname]
    [state(hostname, 'unset', s) for s in states if s in info['status']]
    if ' : ' in info['status']:
        state(hostname, 'unset', 'oldstatus')
    if 'no_panel' in info['status'] or \
            (info['user'] is not None and not info['confirmed']):
        logon(hostname, 'clear_state')
        wait_heartbeat(hostname)

    if user:
        logon(hostname, user)
    else:
        logoff(hostname)

def stop(hostname=None):
    m_list = [hostname] if hostname else machines

    threads = []
    for m in m_list:
        if verbose:
            print("stopping {}".format(m))
        t = Thread(target=lambda: check_output(['docker', 'stop', m]))
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

    cmd = "touch" if action == 'set' else 'rm -f'
    check_call('docker exec {} {} /tmp/{}'.format(hostname, cmd, state).split())

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

if __name__ == "__main__":
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
