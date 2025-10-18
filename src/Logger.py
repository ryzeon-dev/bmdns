import sys
import time
from constants import *

class Logger:
    def __init__(self, persistentLog=False, doLog=True):
        self.doLog = doLog
        if not self.doLog:
            return

        if persistentLog:
            fileName = 'bmdns_' + self.__fmtNow().replace(' ', '_').replace('/', '-').replace(':', '-') + '.log'
            self.filePath = os.path.join(LOG_DIR, fileName)

        else:
            self.filePath = LOG_FILE

        try:
            self.__resetLogFile()
            self._file = open(self.filePath, 'a') # FIXME change back to self.__file

        except:
            print('Fatal: execution attempt without proper install (log directory not found or inaccessible)')
            sys.exit(1)

    def __resetLogFile(self):
        with open(self.filePath, 'w') as file:
            file.write('')

    @staticmethod
    def __fmtNow():
        now = time.localtime()
        return f'{now.tm_year}/{now.tm_mon}/{now.tm_mday} {now.tm_hour}:{now.tm_min}:{now.tm_sec}'

    def alert(self, text):
        if self.doLog:
            print(f'[!] {self.__fmtNow()} | {text}', file=self._file)
            self._file.flush()

    def log(self, text):
        if self.doLog:
            print(f'[*] {self.__fmtNow()} | {text}', file=self._file)
            self._file.flush()

    def error(self, text):
        if self.doLog:
            print(f'[x] {self.__fmtNow()} | {text}', file=self._file)
            self._file.flush()