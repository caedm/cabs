#!/usr/bin/python3

## CABS_Server.py
# This is the webserver that is at the center of the CABS system.
# It is asynchronous, and as such the callbacks and function flow can be a bit confusing
# The basic idea is that the HandleAgentFactory and HandleClienFactory make new HandleAgents and Handle Clients
# There is one per connection, and it processes all communication on that connection, without blocking

from twisted import internet
from twisted.internet.protocol import Factory, Protocol
from twisted.internet import reactor, endpoints, defer, task
from twisted.protocols.basic import LineOnlyReceiver
from twisted.protocols.policies import TimeoutMixin
from twisted.enterprise import adbapi
from twisted.names import client
from twisted.python import log

from shared.clientlib import Clientlib, Reconnect
from shared.broker_response import BrokerResponse, PoolResponse, MachineResponse, ResponseTypes
from shared.client_request import ClientReq, MachineReq, PoolReq, RequestTypes
import ldap
import sys
import logging
import random
import os
import socket
import ssl
import json
import re
from argparse import ArgumentParser
import time
from os.path import dirname, realpath, join

from pymysql import IntegrityError

blacklist = set()
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

random.seed()

settings = {"Max_Clients": '62',
            "Max_Agents": '120',
            "Client_Port": '18181',
            "Agent_Port": '18182',
            "Command_Port": '18183',
            "Agent_Command_Port": '18185',
            "Use_Agents": 'True',
            "Database_Addr": "127.0.0.1",
            "Database_Port": 3306,
            "Database_Usr": "user",
            "Database_Pass": "pass",
            "Database_Name": "test",
            "Reserve_Time": '15',
            "Timeout_Time": '5',
            "Machine_Check": "5",
            "Use_Blacklist": 'False',
            "Auto_Blacklist": 'False',
            "Auto_Max": '300',
            "Auth_Server": '',
            "Auth_Prefix": '',
            "Auth_Postfix": '',
            "Auth_Base": 'None',
            "Auth_Usr_Attr": 'None',
            "Auth_Grp_Attr": 'None',
            "Auth_Secure": 'False',
            "Cert_Dir": "/usr/local/share/cabsbroker/",
            "Auth_Cert": None,
            "Broker_Priv_Key": None,
            "Broker_Cert": None,
            "Agent_Cert": None,
            "RGS_Ver_Min": 'False',
            "Verbose_Out": 'False',
            "Log_Amount": '4',
            "Log_Keep": '600',
            "Log_Time": '1800',
            "One_Connection": 'True',
            "Trusted_Clients": None,
            "Logging_Server": None}


def logoff(trans, host):
    trans.execute("SELECT user FROM current WHERE machine = %s", (host,))
    result = trans.fetchone()
    if result is None:
        return
    user = result[0]
    trans.execute("SET @timedout = (SELECT NOT confirmed FROM current WHERE machine = %(host)s) AND "
                  "(SELECT connecttime FROM current WHERE machine = %(host)s) < "
                  "DATE_SUB(NOW(), INTERVAL %(reserve)s SECOND)",
                  {"host": host, "reserve": settings["Reserve_Time"]})
    trans.execute("DELETE FROM current WHERE machine = %s AND (confirmed OR @timedout)", (host,))
    if trans.rowcount:
        trans.execute("SELECT @timedout")
        result = trans.fetchone()
        if result[0]:
            logger.info("reservation for {} on {} timed out".format(user, host))
        else:
            logger.info("{} logged off of {}".format(user, host))


## Handles each Agent connection
class HandleAgent(LineOnlyReceiver, TimeoutMixin):
    def __init__(self, factory):
        self.factory = factory
        # timeout after 9 seconds
        self.setTimeout(9)

    def connectionMade(self):
        self.agentAddr = self.transport.getPeer()
        self.factory.numConnections = self.factory.numConnections + 1

    def connectionLost(self, reason):
        self.factory.numConnections = self.factory.numConnections - 1

    def lineLengthExceeded(self, line):
        self.transport.abortConnection()

    def lineReceived(self, line):
        # types of reports = status report (sr) and status process report (spr)
        # line: "sr:<hostname>:[user1]:[user2]:[...]
        #       "spr:<proc_status>:<hostname>:[user1]:[user2]:[...]
        try:
            line = line.decode("utf-8")
        except:
            pass
        report = line.split(':')
        reportType = report[0]
        procStatus = None
        if reportType == "spr":
            procStatus = report.pop(1)
        host = report[1]
        users = report[2:]

        if reportType != 'sr' and reportType != 'spr':
            return
        self.updateMachine(host, procStatus)
        self.updateCurrent(host, users)

    @defer.inlineCallbacks
    def updateMachine(self, host, procStatus):
        if procStatus is not None:
            match = re.search(r'([^\d-]*)(-?\d+)', procStatus)
            if match:
                procName, statusId = match.groups()
                statusId = int(statusId)
                # "Unknown" is statusMap[-1]
                statusMap = ["Not Found", "Not Running", "Not Connected", "Okay", "Unknown"]
                procStatus = "{} : {}".format(procName, statusMap[statusId])
        else:
            procStatus = 'Okay'
        result = yield dbpool.runQuery("SELECT status FROM machines WHERE machine = %s", (host,))
        if len(result) == 0:
            # Machine isn't in our database.
            return
        oldStatus = result[0][0]
        dbpool.runQuery("UPDATE machines SET active = True, last_heartbeat = NOW(), "
                        "status = %s WHERE machine = %s", (procStatus, host))
        if oldStatus != procStatus:
            logger.info("status of {} changed from {} to {}".format(
                host, repr(oldStatus), repr(procStatus)))

    @defer.inlineCallbacks
    def updateCurrent(self, host, users):
        if users:
            users = ", ".join(users)
            new_login = yield dbpool.runInteraction(self.is_new_login, host)
            dbpool.runQuery("INSERT INTO current (user, machine, confirmed) " + \
                            "VALUES (%(user)s, %(machine)s, True) ON DUPLICATE KEY " + \
                            "UPDATE confirmed = True, user = %(user)s", {"user": users, "machine": host})
            if new_login:
                logger.info("{} logged into {}".format(users, host))
        else:
            dbpool.runInteraction(logoff, host)

    def is_new_login(self, trans, host):
        trans.execute("SET @reserved = (SELECT NOT confirmed FROM current WHERE machine = %s)",
                      (host,))
        trans.execute("SELECT @reserved IS NULL OR @reserved = True")
        return trans.fetchall()[0][0]


## Creates a HandleAgent for each connection
class HandleAgentFactory(Factory):
    def __init__(self):
        self.numConnections = 0

    def buildProtocol(self, addr):
        # Blacklist check here
        if addr.host in blacklist:
            logger.debug("blacklisted address {0} tried to connect".format(addr.host))
            protocol = DoNothing()
            protocol.factory = self
            return protocol

        # limit connection number here
        if (settings.get("Max_Agents") is not None and settings.get("Max_Agents") != 'None') and (
                int(self.numConnections) >= int(settings.get("Max_Agents"))):
            logger.warning("reached maximum agent connections")
            protocol = DoNothing()
            protocol.factory = self
            return protocol
        return HandleAgent(self)


def create_err_response(message):
    err_response = BrokerResponse()
    err_response.response_type = ResponseTypes.error
    err_response.content = message


# handles each client connection
class HandleClient(LineOnlyReceiver, TimeoutMixin):
    def __init__(self, factory):
        self.factory = factory
        self.setTimeout(9)  # set timeout of 9 seconds

    def connectionMade(self):
        # if auto then add to blacklist
        self.clientAddr = self.transport.getPeer()
        self.factory.numConnections = self.factory.numConnections + 1

    def connectionLost(self, reason):
        self.factory.numConnections = self.factory.numConnections - 1

    def lineLengthExceeded(self, line):
        self.transport.abortConnection()

    def lineReceived(self, line):
        # We can receieve 2 types of lines from a client, poolrequest (pr), machine request(mr)
        # todo: support
        isjson = False

        line = line.decode('utf-8')
        try:
            # handle the updated request format using client objects
            if line[0] == "{":
                request = json.loads(line, object_hook=Clientlib.decode)
                isjson = True
                # self.process_json_request(request)
                user = request.username
                password = request.password
            else:
                request = json.loads(line)
                user = request[1]
                password = request[2]
        except ValueError:
            # fallback for old versions of client
            request = line.split(':')
            user = request[1]
            password = request[2]
        try:
            # get user groups?
            self.groups = (self.user_groups(user, password) if not argv.debug else
                           ['main', 'secondary', 'other'])
        except ldap.INVALID_CREDENTIALS:
            self.send_error("Invalid credentials", isjson)
            return
        except Exception as e:
            logger.error(e)
            self.send_error("Server error", isjson)
            return
        if isjson:
            if request.request_type == RequestTypes.pr:
                self.pool_request(request.username, request.password, request=request)
            elif request.request_type == RequestTypes.mr:
                #     def machine_request(self, user, password, pool, reconnection_preference=None, can_reconnect=False)):
                self.machine_request(request.username, request.password, request.request.pool,
                                     reconnection_preference=request.request.conn_preference, can_reconnect=True)
        else:
            if request[0].startswith('pr'):
                self.pool_request(*request[1:])
            elif request[0] == 'mr':
                self.machine_request(*request[1:])

    @defer.inlineCallbacks
    def pool_request(self, user, password, version=None, request=None):
        # if client name and version are provided then do a lookup for errors
        if version is not None and settings.get('RGS_Ver_Min') != 'False':
            # check version
            if version < settings.get('RGS_Ver_Min'):
                can_reconnect = request is not None
                self.send_error("Sorry, your RGS receiver is out of date, it should be at least {0}".format(
                    settings.get('RGS_Ver_Min')), can_reconnect)
                return
        pools = yield self.available_pools(user, password)
        pools_string = []
        for item in pools:
            pool, description = item
            if description is None:
                description = 'None'
            pools_string.append(str((pool, description)))
            pools_string.append("\n")
        pools_string = ''.join(pools_string)
        response_string = pools_string
        # either send back the pool, description string or compose a server response and send back the json
        if request is not None:
            # if we have a request object, then also perform the client version check
            poolResponse = PoolResponse(pools_string)
            version_err_msg = yield self.client_version_check(request.request.client_name,
                                                              request.request.client_version)
            response = BrokerResponse(ResponseTypes.pr, poolResponse, version_err_msg)
            self.send_response(Clientlib.msgtostr(response))
        self.send_response(response_string)

    @defer.inlineCallbacks
    def client_version_check(self, client_name, client_version):
        query = 'SELECT error_msg from version_check WHERE system_name=%s and version=%s;'
        error_message = yield dbpool.runQuery(query, (client_name, client_version))
        if len(error_message) == 0:
            defer.returnValue(None)
        else:
            defer.returnValue(error_message[0][0])

    @defer.inlineCallbacks
    def machine_request(self, user, password, pool, reconnection_preference=None, can_reconnect=False):
        pools = yield self.available_pools(user, password)
        self.userPools = [p for p, description in pools]
        response = BrokerResponse(response_type=ResponseTypes.mr)
        if pool not in self.userPools:
            self.send_error("{0} does not have access to pool \"{1}\"".format(user, pool), can_reconnect)
            return
        prevMachine = yield self.prev_machine(user, pool)
        # logic to handle case where I have previous machhine and don't want to reconnect. -> respond with a new
        # machine.
        if prevMachine is not None:
            # old client with a previous connection.
            if not can_reconnect:
                logger.info("restored {0} to {1}".format(prevMachine, user))
                dbpool.runQuery("UPDATE current SET connecttime = NOW() WHERE machine = %s", (prevMachine,))
                self.send_machine(prevMachine)

            elif reconnection_preference == Reconnect.Do:
                logger.info("restored {0} to {1}".format(prevMachine, user))
                dbpool.runQuery("UPDATE current SET connecttime = NOW() WHERE machine = %s", (prevMachine,))
                # create broker response with machine request.
                response.content = MachineResponse(machine=prevMachine)
                self.send_response(Clientlib.msgtostr(response))
            elif reconnection_preference == Reconnect.Dont:
                # release the machine, run an auto-it 2 on the machine?
                try:
                    # i want all 3 of these to happen or none to happen -> run them all in a transaction?
                    yield setAutoit("disable2", prevMachine)
                    send_agent_cmd("reboot".encode('utf-8'), prevMachine)
                    # deactivate and log off -> does this prevent the machine from getting picked up in prev_machines?
                    yield dbpool.runInteraction(logoff, prevMachine)
                    machine = yield self.get_open_machine(pool, user,can_reconnect)
                    response.content = MachineResponse(machine=machine, existing_conn=False)
                    self.send_response(Clientlib.msgtostr(response))
                except Exception as e:
                    # send error - will system be in a bad state?
                    print(e)
                    # send a generic error response to the client?
                # we restarted the machine but
                # get a new machine
            elif reconnection_preference == Reconnect.NotSpecified:
                # make a broker request that just responds with a choice fag set.
                response.content = MachineResponse(existing_conn=True)
                self.send_response(Clientlib.msgtostr(response))
        else:
            machine = yield self.get_open_machine(pool, user, can_reconnect)
            if can_reconnect:
                # bundle up the machine in the new message format
                response.content = MachineResponse(machine=machine, existing_conn=False)
                self.send_response(Clientlib.msgtostr(response))
            else:
                self.send_response(machine)

    @defer.inlineCallbacks
    def get_open_machine(self, pool, user, can_reconnect=False):
        openMachines = yield self.open_machines(pool)
        if len(openMachines) == 0:
            self.send_error("Sorry, There are no open machines in {0}.".format(pool), can_reconnect)
            return
        machine = yield self.tryReserve(user, pool, openMachines)
        if machine is None:
            # The chances of this happening are extremely small (see tryReserve).
            self.send_error("RETRY", can_reconnect)
            return
        logger.info("reserved {0} for {1}".format(machine, user))
        return machine

    def send_error(self, message, jsonsupport=False):
        if jsonsupport:
            self.send_response(Clientlib.msgtostr(create_err_response("Err:" + message)))
        else:
            self.transport.write(("Err:" + message).encode('utf-8'))
            self.transport.loseConnection()

    def send_machine(self, machine):
        self.transport.write(machine.encode('utf-8'))
        self.transport.loseConnection()

    @defer.inlineCallbacks
    def prev_machine(self, user, requestedpool):
        # Don't give back a machine that hasn't been confirmed. If a machine is sketchy and the
        # user can't log in, we don't want to give them the same machine when they request
        # another one.

        # NOTE: This query doesn't return confirmed machines correctly
        # query = "SELECT machine FROM current WHERE user = %s AND name = %s AND confirmed = True"

        # NOTE: This is the new and improved code.
        query = (r'SELECT current.machine FROM current LEFT JOIN machines ON '
                 'current.machine = machines.machine '
                 'WHERE user = %s AND confirmed = True AND status LIKE "%%Okay" '
                 'AND (SELECT CONCAT_WS(",", name, secondary) FROM pools WHERE name = %s) '
                 'REGEXP CONCAT("[[:<:]]", machines.name, "[[:>:]]")')

        prevMachine = yield dbpool.runQuery(query, (user, requestedpool))
        if len(prevMachine) == 0:
            defer.returnValue(None)
        else:
            #  TODO: make this return a random machine in the returned set
            defer.returnValue(prevMachine[0][0])

    ## Sends the SQL request to reserve the machine for the user
    def reserveMachine(self, user, pool, machine):
        opstring = "INSERT INTO current VALUES (%s, %s, %s, False, CURRENT_TIMESTAMP)"
        return dbpool.runQuery(opstring, (user, pool, machine))

    @defer.inlineCallbacks
    def tryReserve(self, user, pool, machines):
        # If one machine is being sketchy, we want to lessen the chances of it being assigned repeatedly.
        random.shuffle(machines)
        for machine in machines:
            try:
                yield self.reserveMachine(user, pool, machine)
            except IntegrityError:
                continue
            defer.returnValue(machine)
        defer.returnValue(None)

    def send_response(self, response_string):
        self.transport.write(response_string.encode('utf-8'))
        self.transport.loseConnection()

    # Sends the list of pools accessible to the user
    def writePools(self, listpools):
        for item in listpools:
            pool, description = item
            if description is None:
                description = 'None'
            self.transport.write(str((pool, description)).encode('utf-8'))
            self.transport.write("\n".encode('utf-8'))
        self.transport.loseConnection()

    def user_groups(self, user, password):
        groups = []
        # first bind and then query - should be the same as PHP
        Server = settings.get("Auth_Server") # server.et.byu.edu
        if Server != "":
            if Server.startswith("AUTO"):
                raise ReferenceError("No AUTO Authentication Server yet")
            if not Server.startswith("ldap"):
                Server = "ldap://" + Server
            dn = "cn=" + user + ",ou=accounts,ou=caedm,dc=et,dc=byu,dc=edu"
            searchBase = "dc=et,dc=byu,dc=edu"
            groupAttr = "cn"
            ldap_conn = ldap.initialize(Server)
            ldap_conn.start_tls_s()
            ldap_conn.bind_s(dn, password, ldap.AUTH_SIMPLE) # login
            r = ldap_conn.search(searchBase, ldap.SCOPE_SUBTREE, "memberuid=" + user)
            results = ldap_conn.result(r,9)
            groups = list(map(lambda grptuple : grptuple[1][groupAttr][0].decode("utf-8"), results[1]))
            ldap_conn.unbind()
            # get user info

            # DN = settings.get("Auth_Prefix") + user + settings.get("Auth_Postfix")
            # Base = settings.get("Auth_Base")
            # Scope = ldap.SCOPE_SUBTREE
            # Attrs = [settings.get("Auth_Grp_Attr")]
            # UsrAttr = settings.get("Auth_Usr_Attr")
            # if settings.get("Auth_Secure") == 'True':
            #     if settings.get("Auth_Cert") != 'None' and settings.get("Auth_Cert") is not None:
            #         ldap.set_option(ldap.OPT_X_TLS_CACERTFILE, settings.get("Auth_Cert"))
            #         ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_DEMAND)
            #     else:
            #         ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            # l = ldap.initialize(Server)
            # l.set_option(ldap.OPT_REFERRALS, 0)
            # l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
            # if settings.get("Auth_Secure") == 'True':
            #     l.start_tls_s()
            # l.bind_s(DN, password, ldap.AUTH_SIMPLE)
            # r = l.search(Base, Scope, UsrAttr + '=' + user, Attrs)
            # result = l.result(r, 9)
            # # TODO: remove or improve this try block. unbind() will throw ldap.LDAPError if it's called twice;
            # # maybe that's why it's here. Would that ever happen here?
            # try:
            #     l.unbind()
            # except:
            #     pass
            #
            # # get user groups
            # AttrsDict = result[1][0][1]
            # for key in AttrsDict:
            #     for x in AttrsDict[key]:
            #         # take only the substring after the first =, and before the comma
            #         groups.append(x[x.find('=') + 1:x.find(',')])

        return groups

    def available_pools(self, user, password):
        query = ("SELECT name, description FROM pools WHERE deactivated = False AND "
                 "(groups IS NULL")
        if len(self.groups) > 0:
            query += " OR groups REGEXP %s)"
            regexstring = "|".join("(.*{0}.*)".format(group) for group in self.groups)
            return dbpool.runQuery(query, (regexstring,))
        else:
            query += ")"
            return dbpool.runQuery(query)

    ## Runs the SQL to get machines the user could use
    @defer.inlineCallbacks
    def open_machines(self, requestedPool):
        poolRegex = lambda pools: "|".join("(^{}$)".format(pool) for pool in pools)
        query = "SELECT machine FROM machines WHERE name REGEXP %s AND machine NOT IN " + \
                "(SELECT machine FROM current) AND active = True AND status LIKE '%%Okay' AND " + \
                "deactivated = False"
        result = yield dbpool.runQuery(query, [poolRegex([requestedPool])])
        if len(result) == 0:
            secondaries = yield dbpool.runQuery("SELECT secondary FROM pools WHERE name = %s",
                                                [requestedPool])
            if secondaries[0][0] is not None:
                pools = [requestedPool] + [pool for pool in secondaries[0][0].split(',')
                                           if pool in self.userPools]
                result = yield dbpool.runQuery(query, [poolRegex(pools)])
        machines = [record[0] for record in result]
        defer.returnValue(machines)


## A place to direct blacklisted addresses, or if we have too many connections at once
class DoNothing(Protocol):
    def makeConnection(self, transport):
        transport.abortConnection()


## creates a HandleClient for each Client connection
class HandleClientFactory(Factory):
    def __init__(self):
        self.numConnections = 0
        self.transports = []

    def buildProtocol(self, addr):
        # Blacklist check here
        if addr.host in blacklist:
            logger.debug("blacklisted address {0} tried to connect".format(addr.host))
            protocol = DoNothing()
            protocol.factory = self
            return protocol

        # limit connection number here
        if ((settings.get("Max_Clients") is not None and settings.get("Max_Clients") != 'None') and
                (int(self.numConnections) >= int(settings.get("Max_Clients")))):
            logger.warning("reached maximum Client connections")
            protocol = DoNothing()
            protocol.factory = self
            return protocol
        return HandleClient(self)


def send_agent_cmd(command, hostname):
    port = int(settings["Agent_Command_Port"])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostname, port))
    if settings.get("Broker_Cert") is None:
        s_wrapped = s
    else:
        ssl_cert = settings.get("Agent_Cert")
        s_wrapped = ssl.wrap_socket(s, certfile=settings["Broker_Cert"],
                                    keyfile=settings["Broker_Priv_Key"], cert_reqs=ssl.CERT_REQUIRED,
                                    ca_certs=ssl_cert, ssl_version=ssl.PROTOCOL_SSLv23)
    s_wrapped.sendall(str(command + "\r\n").encode('utf-8'))


# exception classes for auto-it
class AutoitUnknownMachine(Exception):
    pass


class AutoitBadCommand(Exception):
    pass


@defer.inlineCallbacks
def setAutoit(action, hostname):
    result = yield dbpool.runQuery("SELECT deactivated,reason FROM machines WHERE machine = %s",
                                   (hostname,))
    if len(result) == 0:
        raise AutoitUnknownMachine

    if action == "enable":
        dbpool.runQuery("UPDATE machines SET deactivated = FALSE, reason = NULL WHERE machine = %s",
                        (hostname,))
    elif re.match(re.compile("disable[0-9]"), action):
        print("disabling machine (" + action + ")")
        reason = "'autoit " + action[-1:] + " " + time.strftime("%m/%d/%Y") + "'"
        dbpool.runQuery("UPDATE machines SET deactivated = TRUE, reason = " + \
                        reason + " WHERE machine = %s", (hostname,))
    else:
        raise AutoitBadCommand


class CommandHandler(LineOnlyReceiver):
    """Recognized commands:
    query[:verbose]
    tell_agent:(restart|reboot):<hostname>
    autoit:(enable|disable0|disable1|disable2|disable3):<hostname>
    ruok
    """

    commands = ('query', 'tell_agent', 'autoit', 'dump', 'ruok')

    log_levels = {'debug': ['query', 'dump', 'ruok'],
                  'info': ['tell_agent', 'autoit']}

    def lineReceived(self, line):
        # parse
        try:
            line = line.decode("utf-8")
        except:
            pass
        segments = line.split(':')
        command = segments[0]
        args = segments[1:]

        # validate
        if command not in CommandHandler.commands:
            self.bad_command(line)
            return

        # log
        log_levels = {command: level for level, command_list in CommandHandler.log_levels.items()
                      for command in command_list}
        msg = "received command from {}: '{}'".format(self.transport.getPeer(), line.strip())
        if settings.get("Logging_Server") == None or self.transport.getPeer() != settings.get("Logging_Server"):
            getattr(logger, log_levels[command])(msg)

        # execute
        try:
            getattr(self, command)(*args)
        except (TypeError, ValueError) as e:
            # Incorrect arguments.
            self.bad_command(line)

    def query(self, verbose=False):
        # validate args
        if verbose and verbose != 'verbose':
            raise ValueError
        verbose = bool(verbose)

        response = dbpool.runQuery(
            "SELECT machines.name, machines.machine, status, user, deactivated, reason " + \
            "FROM machines LEFT OUTER JOIN current ON machines.machine = current.machine")
        response.addCallback(self.respond_query, verbose)

    def respond_query(self, response, verbose):
        str_response = ""
        if verbose:
            str_response += "pool, machine, status, has users, deactivated, reason\n"
        for line in response:
            str_response += ','.join([str(x) for x in line[:3]])
            str_response += ',1,' if line[3] is not None else ',0,'
            str_response += ','.join([str(x) for x in line[4:]])
            str_response += '\n'
        self.transport.write("\n".encode('utf-8'))
        self.transport.write(str_response[:-1].encode('utf-8'))
        self.transport.loseConnection()

    @defer.inlineCallbacks
    def dump(self):
        keys = "pool status user deactivated reason confirmed connecttime last_heartbeat".split()
        type_map = {"confirmed": bool,
                    "deactivated": bool,
                    "connecttime": str,
                    "last_heartbeat": str}
        convert = lambda key, val: type_map[key](val) if key in type_map else val

        response = yield dbpool.runQuery(
            "SELECT machines.machine, machines.name, status, user, deactivated, reason, "
            "confirmed, connecttime, last_heartbeat "
            "FROM machines LEFT OUTER JOIN current ON machines.machine = current.machine")

        data = {line[0]: {key: convert(key, val) for key, val in zip(keys, line[1:])}
                for line in response}

        self.transport.write("\n".encode('utf-8'))
        self.transport.write(json.dumps(data))
        self.transport.loseConnection()

    @defer.inlineCallbacks
    def autoit(self, action, hostname):
        try:
            yield setAutoit(action, hostname)
        except AutoitUnknownMachine:
            self.transport.write("\n".encode('utf-8'))
            self.transport.write("unknown machine: " + hostname.encode('utf-8'))
            self.tranport.loseConnection()
            return
        except AutoitBadCommand:
            self.bad_command(":".join(("autoit", action, hostname)))

    def bad_command(self, command):
        logger.info("received bad command: '" + command + "'")
        self.transport.write("\n".encode('utf-8'))
        self.transport.write(str("unrecognized command: " + command).encode('utf-8'))
        self.transport.loseConnection()

    def tell_agent(self, command, hostname):
        try:
            send_agent_cmd(command, hostname)
        except socket.error as e:
            print(e)
            logger.warning("couldn't send command to " + hostname)
            self.transport.write("\n".encode('utf-8'))
            self.transport.write("Couldn't connect to {}.".format(hostname).encode('utf-8'))
            self.transport.loseConnection()
            return

    def ruok(self):
        print("imok")
        self.transport.write("\n".encode('utf-8'))
        self.transport.write("imok\n".encode('utf-8'))
        self.transport.loseConnection()


@defer.inlineCallbacks
def checkMachines():
    if settings["Timeout_Time"] is None or settings["Timeout_Time"] == 'None':
        return
    result = yield dbpool.runInteraction(disable_machines)
    for machine, user in result:
        if user is None:
            logger.warning("{} went inactive".format(machine))
        else:
            logger.warning("{} went inactive while {} was logged in".format(machine, user))


def disable_machines(trans):
    trans.execute("SET @cutoff = DATE_SUB(NOW(), INTERVAL %s SECOND)", (settings["Timeout_Time"],))
    trans.execute("DROP TABLE IF EXISTS inactive")
    trans.execute("CREATE TEMPORARY TABLE inactive AS "
                  "(SELECT machines.machine, current.user FROM machines LEFT JOIN current ON "
                  " machines.machine = current.machine WHERE active = True AND last_heartbeat < @cutoff)")
    trans.execute("UPDATE machines SET active = False, status = NULL WHERE machine IN "
                  "(SELECT machine FROM inactive)")
    trans.execute("INSERT INTO inactive SELECT machine, user FROM current WHERE connecttime < @cutoff "
                  " AND machine NOT IN (SELECT machine FROM machines)")
    trans.execute("DELETE FROM current WHERE machine IN (SELECT machine FROM inactive)")
    trans.execute("SELECT * FROM inactive")
    return trans.fetchall()


## Gets the blacklist from the database, and updates is
def cacheBlacklist():
    querystring = ("SELECT blacklist.address FROM blacklist LEFT JOIN whitelist "
                   "ON blacklist.address = whitelist.address WHERE (banned = True "
                   "AND whitelist.address IS NULL)")
    r = dbpool.runQuery(querystring)
    r.addBoth(setBlacklist)


## Sets the blacklist variable, given data from the Database
def setBlacklist(data):
    global blacklist
    blacklist = set()
    for item in data:
        blacklist.add(item[0])


## Chooses a LDAP/Active Directory server
def setAuthServer(results):
    results = results[0]
    if not results[0].payload.target:
        logger.error("could not find LDAP server from AUTO")
    else:
        settings["Auth_Server"] = str(results[0].payload.target)


## Does a DNS service request for an LDAP service
def getAuthServer():
    domain = settings.get("Auth_Auto").replace('AUTO', '', 1)
    domain = '_ldap._tcp' + domain
    resolver = client.Resolver('/etc/resolv.conf')
    d = resolver.lookupService(domain)
    d.addCallback(setAuthServer)


## Reads the configuration file
def readConfigFile():
    # open the .conf file and return the variables as a dictionary
    filelocation = join(dirname(realpath(__file__)), "cabsbroker.conf")
    if not os.path.isfile(filelocation):
        return
    with open(filelocation, 'r') as f:
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
            if val == "None":
                val == None
            settings[key] = val
        f.close()

    for key in ("Broker_Cert", "Broker_Priv_Key", "Agent_Cert", "Trusted_Clients"):
        if settings[key] is not None and not os.path.isabs(settings[key]):
            settings[key] = os.path.join(settings["Cert_Dir"], settings[key])
    if settings["Broker_Priv_Key"] is None:
        settings["Broker_Priv_Key"] = settings["Broker_Cert"]


## gets additional settings overrides from the Database
def readDatabaseSettings():
    # This needs to be a "blocked" call to ensure order, it can't be asynchronous.
    querystring = "SELECT * FROM settings"
    con = dbpool.connect()
    cursor = con.cursor()
    cursor.execute(querystring)
    data = cursor.fetchall()

    global settings
    for rule in data:
        settings[str(rule[0])] = rule[1]

    cursor.close()
    dbpool.disconnect(con)

    con = dbpool.connect()
    cursor = con.cursor()
    querystring = "UPDATE settings SET applied = True"
    cursor.execute(querystring)
    # data = cursor.fetchall()
    cursor.close()
    con.commit()
    dbpool.disconnect(con)


## See if we need to restart because Database settings have changed
def checkSettingsChanged():
    querystring = "select COUNT(*) FROM settings WHERE (applied = False OR applied IS NULL)"
    r = dbpool.runQuery(querystring)
    r.addBoth(getSettingsChanged)


## Sees the result from checkSettingsChanged, and acts accordingly
def getSettingsChanged(data):
    if int(data[0][0]) > 0:
        reactor.stop()
        # should probably sleep here for a few seconds?
        os.execv(__file__, sys.argv)


## A logging.Handler class for writing out log to the Database
class MySQLHandler(logging.Handler):
    # This is our logger to the Database, it will handle out logger calls
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        querystring = "INSERT INTO log VALUES(NOW(), %s, %s, DEFAULT)"
        r = dbpool.runQuery(querystring, (str(record.getMessage()), record.levelname))


## Makes sure the log doesn't grow too big, removes execess
def pruneLog():
    querystring = ("DELETE FROM log WHERE id <= (SELECT id FROM (SELECT id FROM log "
                   "ORDER BY id DESC LIMIT 1 OFFSET %s)foo )")
    r = dbpool.runQuery(querystring, (int(settings.get("Log_Keep")),))


## Starts the logging
def setLogging():
    global logger
    loglevel = int(settings.get("Log_Amount"))
    if loglevel <= 0:
        loglevel = logging.CRITICAL
        # For our purposes, CRITICAL means no logging
    elif loglevel == 1:
        loglevel = logging.ERROR
    elif loglevel == 2:
        loglevel = logging.WARNING
    elif loglevel == 3:
        loglevel = logging.INFO
    elif loglevel >= 4:
        loglevel = logging.DEBUG
    logger.setLevel(loglevel)

    if settings.get("Verbose_Out") == 'True':
        logger.addHandler(logging.StreamHandler(sys.stdout))

    logger.addHandler(MySQLHandler())


def start_ssl_cmd_server():
    with open(settings["Broker_Cert"], 'r') as certfile:
        certdata = certfile.read()
    if settings["Broker_Priv_Key"] != settings["Broker_Cert"]:
        with open(settings.get("Broker_Priv_Key"), 'r') as keyfile:
            certdata += keyfile.read()
    with open(settings["Trusted_Clients"], 'r') as f:
        authdata = f.read()
    certificate = internet.ssl.PrivateCertificate.loadPEM(certdata)
    authority = internet.ssl.Certificate.loadPEM(authdata)
    factory = Factory.forProtocol(CommandHandler)
    reactor.listenSSL(int(settings.get("Command_Port")), factory, certificate.options(authority))


if __name__ == "__main__":
    global argv
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    argv = parser.parse_args()

    # Read the settings
    readConfigFile()

    # create database pool
    global dbpool
    dbpool = adbapi.ConnectionPool(
        "pymysql",
        db=settings.get("Database_Name"),
        port=int(settings.get("Database_Port")),
        user=settings.get("Database_Usr"),
        passwd=settings.get("Database_Pass"),
        host=settings.get("Database_Addr"),
        cp_reconnect=True
    )

    # get override settings from the database, then start logger
    readDatabaseSettings()
    # SetLogging
    setLogging()
    logger.info("starting up")

    if settings.get("Broker_Priv_Key") is None or settings.get("Broker_Cert") is None:
        # Create Client Listening Server
        serverstring = "tcp:" + str(settings.get("Client_Port"))
        endpoints.serverFromString(reactor, serverstring).listen(HandleClientFactory())

        # Create external command Listening Server
        endpoint = endpoints.TCP4ServerEndpoint(reactor, int(settings.get("Command_Port")))
        endpoint.listen(Factory.forProtocol(CommandHandler))
    else:
        serverstring = "ssl:" + str(settings.get("Client_Port")) + ":privateKey=" + \
                       settings.get("Broker_Priv_Key") + ":certKey=" + settings.get("Broker_Cert")
        endpoints.serverFromString(reactor, serverstring).listen(HandleClientFactory())
        start_ssl_cmd_server()

    # Set up Agents listening
    if (settings.get("Use_Agents") == 'True'):
        # Use Agents, so start the listening server
        if settings.get("Broker_Priv_Key") is None or settings.get("Broker_Cert") is None:
            agentserverstring = "tcp:" + str(settings.get("Agent_Port"))
            endpoints.serverFromString(reactor, agentserverstring).listen(HandleAgentFactory())
        else:
            agentserverstring = "ssl:" + str(settings.get("Agent_Port")) + ":privateKey=" + \
                                settings.get("Broker_Priv_Key") + ":certKey=" + settings.get("Broker_Cert")
            endpoints.serverFromString(reactor, agentserverstring).listen(HandleAgentFactory())

        checkup = task.LoopingCall(checkMachines)
        checkup.start(int(settings["Machine_Check"]))
    else:
        # this to do so things kinda work without agents
        querystring = "UPDATE machines SET active = True, status = 'Okay'"
        r1 = dbpool.runQuery(querystring)

    # resolve LDAP server
    if settings.get("Auth_Server").startswith("AUTO"):
        settings["Auth_Auto"] = settings.get("Auth_Server")
        resolveldap = task.LoopingCall(getAuthServer)
        # Get the LDAP server every 2 hours
        resolveldap.start(7200)

    # Start Blacklist cacheing
    if settings.get("Use_Blacklist") == 'True':
        getblacklist = task.LoopingCall(cacheBlacklist)
        # refresh blacklist every 15 minutes
        getblacklist.start(900)
    # Start Pruning log
    if int(settings.get("Log_Amount")) != 0:
        prune = task.LoopingCall(pruneLog)
        prune.start(int(settings.get("Log_Time")))

    # Check the online settings every 9 minutes, and restart if they changed
    checksettingschange = task.LoopingCall(checkSettingsChanged)
    checksettingschange.start(540)

    # Start Everything
    reactor.run()
