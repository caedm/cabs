class RequestTypes:
    mr = 'mr'
    pr = 'pr'


class PoolReq:
    def __init__(self, client_version=None, client_name=None, sender_version=None):
        self.client_version = client_version
        self.client_name = client_name
        self.sender_version = sender_version


class MachineReq:
    def __init__(self, protocol_version=None, conn_preference=None, pool=None):
            self.protocol_version = protocol_version
            self.conn_preference = conn_preference
            self.pool = pool


class ClientReq:
    def __init__(self, request=None, request_type=None, username=None, password=None):
        self.request = request
        self.request_type = request_type
        self.username = username
        self.password = password