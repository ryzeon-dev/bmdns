from utils import *

class DnsRecord:
    def __init__(self):
        self.name = b''
        self.type = 0       # u16
        self.class_ = 0     # u16
        self.ttl = 0        # u32
        self.dataSize = 0   # u16
        self.data = b''

        self.byteSize = 0

    @staticmethod
    def fromBytes(bytes):
        index = 0
        self = DnsRecord()

        self.name = getNameBytes(bytes)
        index += len(self.name)

        self.type = bytesToU16(bytes[index:index+2])
        index += 2

        self.class_ = bytesToU16(bytes[index:index+2])
        index += 2

        self.ttl = bytesToU32(bytes[index:index+4])
        index += 4

        self.dataSize = bytesToU16(bytes[index:index+2])
        index += 2

        for _ in range(self.dataSize):
            self.data += bytes[index:index+1]
            index += 1

        self.byteSize += index
        return self

    def toBytes(self):
        bytes = b''

        bytes += self.name
        bytes += u16ToBytes(self.type)

        bytes += u16ToBytes(self.class_)
        bytes += u32ToBytes(self.ttl)

        bytes += u16ToBytes(self.dataSize)
        bytes += self.data

        return bytes

    def __repr__(self):
        return f'DnsRecord( {self.name = } ; {self.type = } ; {self.class_ = } ; {self.ttl = } ; {self.dataSize = } ; {self.data} )'