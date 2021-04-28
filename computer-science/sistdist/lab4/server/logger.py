from datetime import datetime

LEVEL_NONE = 'none'
LEVEL_INFO = 'info'
LEVEL_WARNING = 'warning'
LEVEL_ERROR = 'error'


class Colors:
    header = '\033[95m'
    white = '\033[1;37m'
    blue = '\033[94m'
    lblue = '\033[1;34m'
    cyan = '\033[96m'
    gray = '\033[1;30m'
    purple = '\033[0;35m'
    green = '\033[92m'
    yellow = '\033[93m'
    fail = '\033[91m'
    reset = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


class Logger():
    '''This class provides more detailed prints and with colors. '''
    def __init__(self, level=LEVEL_INFO):
        self.level = level

    def info(self, *args):
        if(self.level == LEVEL_INFO):
            print(Colors.cyan + datetime.now().__str__()[:19], 'INFO:', *args, Colors.reset)
    
    def success(self, *args):
        if(self.level == LEVEL_INFO):
            print(Colors.green + datetime.now().__str__()[:19], 'INFO:', *args, Colors.reset)

    def warning(self, *args):
        if(self.level in [LEVEL_INFO, LEVEL_WARNING]):
            print(Colors.warning + datetime.now().__str__()[:19], 'WARNING:', *args, Colors.reset)

    def error(self, *args):
        print(Colors.FAIL + datetime.now().__str__()[:19], 'ERROR:', *args, Colors.reset)


