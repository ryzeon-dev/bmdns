from DnsResponse import DnsResponse
from utils import decodeName

class Cache:
    def __init__(self):
        self.__cache = {}

    def has(self, qname):
        return qname in self.__cache

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
        self.__cache[qname] = response

    def getFotId(self, qname, id):
        response: DnsResponse = self.__cache.get(qname)

        if response is None:
            return

        bytes = response.packForId(id)
        if bytes is None:
            self.__cache.pop(qname)
            return None

        return bytes