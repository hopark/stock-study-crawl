from requests import Session


class MySession(Session):
    def __init__(self):
        super().__init__()

    def setOptions(self, headers=None, timeout=None, verify=None, proxies=None):
        if headers != None:
            self.headers = headers
        if timeout != None:
            self.timeout = timeout
        if verify != None:
            self.verify = verify
        if proxies != None:
            self.proxies = proxies
