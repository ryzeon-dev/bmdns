from DnsHeader import DnsHeader
from DnsQuestion import DnsQuestion
from DnsRecord import DnsRecord
from utils import u16ToBytes
import time

class DnsResponse:
    def __init__(self, bytes):
        self.fullBytes = bytes
        self.header = DnsHeader.fromBytes(bytes)
        self.question = DnsQuestion.fromBytes(bytes[self.header.byteSize:])
        self.firstAnswer = DnsRecord.fromBytes(bytes[self.header.byteSize + self.question.byteSize:])

        self.ttl = self.firstAnswer.ttl
        self.qname = self.question.qname
        self.insertionTime = time.time()

    def _isValid(self):
        return time.time() < (self.insertionTime + self.ttl)

    def packForId(self, id):
        if not self._isValid():
            return None

        return u16ToBytes(id) + self.fullBytes[2:]

    def __repr__(self):
        return f'DnsResponse(qname: {self.qname}, ttl: {self.ttl}, remaining: {(self.insertionTime + self.ttl) - time.time()})'