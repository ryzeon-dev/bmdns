import sys
from constants import *
from utils import fmtNow

RED = '\x1b[91m'
GREEN = '\x1b[92m'
YELLOW = '\x1b[93m'
RESET = '\x1b[00m'

class Logger:
    def __init__(self, persistentLog=False, doLog=True, colorLog=True):
        self.doLog = doLog
        self.colorLog = colorLog

        if not self.doLog:
            return

        if persistentLog:
            fileName = 'bmdns_' + fmtNow().replace(' ', '_').replace('/', '-').replace(':', '-') + '.log'
            self.filePath = os.path.join(LOG_DIR, fileName)

        else:
            self.filePath = LOG_FILE

        try:
            self.__resetLogFile()
            self._file = open(self.filePath, 'a')

        except:
            print('Fatal: execution attempt without proper install (log directory not found or inaccessible)')
            sys.exit(1)

    def __resetLogFile(self):
        with open(self.filePath, 'w') as file:
            file.write('')

    def alert(self, text):
        if self.doLog:
            statusAndTimestamp = f'{YELLOW}[!] {fmtNow()} {RESET}' if self.colorLog else f'[!] {fmtNow()}'
            print(f'{statusAndTimestamp} | {text}', file=self._file)
            self._file.flush()

    def log(self, text):
        if self.doLog:
            statusAndTimestamp = f'{GREEN}[*] {fmtNow()} {RESET}' if self.colorLog else f'[*] {fmtNow()}'
            print(f'{statusAndTimestamp} | {text}', file=self._file)
            self._file.flush()

    def error(self, text):
        if self.doLog:
            statusAndTimestamp = f'{RED}[x] {fmtNow()} {RESET}' if self.colorLog else f'[x] {fmtNow()}'
            print(f'{statusAndTimestamp} | {text}', file=self._file)
            self._file.flush()