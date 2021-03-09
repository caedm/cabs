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

# class RequestEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__dict__
        
# def requestDecode(request_dict):
#     return namedtuple('_', request_dict.keys())(*request_dict.values())


# pr = PoolReq("1.0", "mac_rgs_connect", "1.3")
# cr = ClientReq(pr, "pr")
# reqJson = json.dumps(cr, indent=4,cls=RequestEncoder)
# print(reqJson)
# reqObj = json.loads(reqJson, object_hook=requestDecode)
# print(reqObj.request_type, reqObj.request.client_name)

# example usage
'''
req = ClientReq('1.123', 'mac_labconnect', ['ssh', 'rgs', 'rdp'], 'pr', '1.1')

// req to json string
reqJson = json.dumps(req,indent=4,cls=ClientReqEncoder)

// reqJson back to object
reqObj = json.loads(reqJson, object_hook=decodeClientReq)
'''