import sys
import time

from constants import *
from utils import fmtNow

class Logger:
    def __init__(self, persistentLog=False, doLog=True):
        self.doLog = doLog
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
            print(f'[!] {fmtNow()} | {text}', file=self._file)
            self._file.flush()

    def log(self, text):
        if self.doLog:
            print(f'[*] {fmtNow()} | {text}', file=self._file)
            self._file.flush()

    def error(self, text):
        if self.doLog:
            print(f'[x] {fmtNow()} | {text}', file=self._file)
            self._file.flush()