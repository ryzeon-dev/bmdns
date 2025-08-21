from DnsResponse import DnsResponse
from utils import decodeName
from threading import Semaphore, Timer

class Cache:
    def __init__(self):
        self.__mutex = Semaphore(1)
        self.__cache = {}

        self.timer = Timer(5, self._flush, ())
        self.timer.start()

    def append(self, bytes):
        if not bytes:
            return

        try:
            response = DnsResponse(bytes)

        except:
            return

        if response.ttl == 0:
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

        for qname, dnsResponse in self.__cache.items():
            if not dnsResponse._isValid():
                self.__cache.pop(qname)

        self.__mutex.release()
        self.timer.run()