class AuthenticationFailedError(Exception):
    def __init__(self, msg):
        self.message = msg


class RequestInvalidError(Exception):
    def __init__(self, code=400, msg=''):
        self.status_code = code
        self.message = msg
