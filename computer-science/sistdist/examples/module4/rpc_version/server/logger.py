from datetime import datetime

LEVEL_NONE = 'none'
LEVEL_INFO = 'info'
LEVEL_WARNING = 'warning'
LEVEL_ERROR = 'error'

class Logger():
    def __init__(self, level=LEVEL_INFO):
        self.level = level

    def info(self, *args):
        if(self.level == LEVEL_INFO):
            print(datetime.now().__str__()[:19], 'INFO:', *args)
    
    def cyan(self, *args):
        if(self.level == LEVEL_INFO):
            print(bcolors.OKCYAN + datetime.now().__str__()[:19], 'INFO:', *args, bcolors.ENDC)
    
    def success(self, *args):
        if(self.level == LEVEL_INFO):
            print(bcolors.OKGREEN + datetime.now().__str__()[:19], 'INFO:', *args, bcolors.ENDC)

    def warning(self, *args):
        if(self.level in [LEVEL_INFO, LEVEL_WARNING]):
            print(bcolors.WARNING + datetime.now().__str__()[:19], 'WARNING:', *args, bcolors.ENDC)

    def error(self, *args):
        print(bcolors.FAIL + datetime.now().__str__()[:19], 'ERROR:', *args, bcolors.ENDC)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'