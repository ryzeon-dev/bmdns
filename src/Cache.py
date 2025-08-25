from DnsResponse import DnsResponse
from utils import decodeName
from constants import *

from threading import Semaphore, Thread
import time

class Cache:
    def __init__(self):
        self.__mutex = Semaphore(1)
        self.__cache = {}

        self.flushThread = Thread(target=self._flush, args=())
        self.flushThread.start()

    def append(self, bytes):
        if not bytes:
            return

        try:
            response = DnsResponse(bytes)

        except Exception as e:
            return

        if response.ttl == 0 or (
            response.question.qtype != QUESTIONTYPE_A and response.question.qtype != QUESTIONTYPE_CNAME
        ):
            return

        qname = decodeName(response.qname, 0)
        self.__mutex.acquire()

        self.__cache[qname] = response
        self.__mutex.release()

    def getForId(self, qname, id):
        self.__mutex.acquire()
        response: DnsResponse = self.__cache.get(qname)
        self.__mutex.release()

        if response is None:
            return

        # if the result is None, it means the TTL is expired
        bytes = response.packForId(id)
        if bytes is None:
            self.__mutex.acquire()
            self.__cache.pop(qname)
            self.__mutex.release()
            return None

        return bytes

    def _flush(self):
        self.__mutex.acquire()
        cacheItems = list(self.__cache.items())

        for qname, dnsResponse in cacheItems:
            if not dnsResponse._isValid():
                try: self.__cache.pop(qname)
                except: pass

        self.__mutex.release()
        time.sleep(FLUSH_TIMEOUT)
        self._flush()

    def __repr__(self):
        return f'Cache({self.__cache})'