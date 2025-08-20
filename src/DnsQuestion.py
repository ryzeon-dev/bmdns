import struct
from utils import *

class DnsQuestion:
    def __init__(self):
        self.qname = b''
        self.qtype = 0
        self.qclass = 0

        self.byteSize = 0

    @staticmethod
    def fromBytes(bytes):
        index = 0
        self = DnsQuestion()

        self.qname = getNameBytes(bytes)
        index += len(self.qname)

        self.qtype = bytesToU16(bytes[index:index+2])
        index += 2

        self.qclass = bytesToU16(bytes[index:index+2])

        index += 2

        self.byteSize = index
        return self

    def toBytes(self):
        bytes = b''

        bytes += self.qname
        bytes += u16ToBytes(self.qtype)
        bytes += u16ToBytes(self.qclass)

        return bytes