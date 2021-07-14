class ResponseTypes:
    mr = 'mr'
    pr = 'pr'
    error = 'err'


class PoolResponse:
    # response contains responses to queries, t/f in dictionary.
    # response_type: mr, pr 
    # response data: machine name or pools list
    # error: error if error ocurred
    # pool response, machine response separately?
    def __init__(self, pools_string):
        self.pools_string = pools_string


class MachineResponse:
    def __init__(self, machine=None, existing_conn=False):
        self.machine = machine
        self.existing_conn = existing_conn


class BrokerResponse:
    def __init__(self, response_type=None, content=None, version_err_msg=None):
        self.response_type = response_type
        self.content = content
        self.version_err_msg = version_err_msg
