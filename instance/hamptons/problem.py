
class Problem(Exception):
    ''' "I haven't even begun to problem." -Liz Lemon
    '''
    def __init__(self, value, msg=None, etc=None):
        self.value = value
        self.msg = msg
        self.etc = etc
    def __str__(self):
        return repr(self.value)