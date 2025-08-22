import time

LOG_FILE = '/usr/local/share/bmdns/bmdns.log'

class Logger:
    def __init__(self):
        self.__resetLogFile()
        self.__file = open(LOG_FILE, 'a')

    def __resetLogFile(self):
        with open(LOG_FILE, 'w') as file:
            file.write('')

    def __fmtNow(self):
        now = time.localtime()
        return f'{now.tm_year}/{now.tm_mon}/{now.tm_mday} {now.tm_hour}:{now.tm_min}:{now.tm_sec}'

    def alert(self, text):
        print(f'[!] {self.__fmtNow()} | {text}', file=self.__file)
        self.__file.flush()

    def log(self, text):
        print(f'[*] {self.__fmtNow()} | {text}', file=self.__file)
        self.__file.flush()

    def error(self, text):
        print(f'[x] {self.__fmtNow()} | {text}', file=self.__file)
        self.__file.flush()