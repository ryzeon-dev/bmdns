from constants import RCODE_SERVER_REFUSAL
from utils import *

class DnsHeader:
    def __init__(self):
        self.id = 0                 # u16
        self.qr = 0                 # u1
        self.opcode = 0             # u4
        self.flagAA = 0             # u1
        self.flagTC = 0             # u1
        self.flagRD = 0             # u1
        self.flagRA = 0             # u1
        self.Z = 0                  # u3
        self.rcode = 0              # u4
        self.questionsCount = 0     # u16
        self.answersCount = 0       # u16
        self.nameServersCount = 0   # u16
        self.additionalsCount = 0   # u16

        # const
        self.byteSize = 12

    @staticmethod
    def fromBytes(bytes):
        index = 0
        self = DnsHeader()

        self.id = bytesToU16(bytes[index:index+2])
        index += 2

        opcodeAndFlags = bytes[index]
        index += 1

        self.qr = checkBitFlag(opcodeAndFlags, 0b10000000)
        self.opcode = opcodeAndFlags & 0b01111000
        self.flagAA = checkBitFlag(opcodeAndFlags, 0b00000100)
        self.flagTC = checkBitFlag(opcodeAndFlags, 0b00000010)
        self.flagRD = checkBitFlag(opcodeAndFlags, 0b00000001)

        rcodeAndFlags = bytes[index]
        index += 1

        self.flagRA = checkBitFlag(rcodeAndFlags, 0b10000000)
        self.rcode = rcodeAndFlags & 0b00001111

        self.questionsCount = bytesToU16(bytes[index:index+2])
        index += 2

        self.answersCount = bytesToU16(bytes[index:index+2])
        index += 2

        self.nameServersCount = bytesToU16(bytes[index:index+2])
        index += 2

        self.additionalsCount = bytesToU16(bytes[index:index+2])
        index += 2

        return self

    def toBytes(self):
        bytes = b''

        bytes += u16ToBytes(self.id)

        opcodeAndFlags = 0
        opcodeAndFlags |= 0b10000000 if self.qr else 0
        opcodeAndFlags |= (self.opcode & 0b01111000)
        opcodeAndFlags |= 0b00000100 if self.flagAA else 0
        opcodeAndFlags |= 0b00000010 if self.flagTC else 0
        opcodeAndFlags |= 0b00000001 if self.flagRD else 0

        bytes += struct.pack('!B', opcodeAndFlags)

        rcodeAndFlags = 0
        rcodeAndFlags |= 0b10000000 if self.flagRA else 0
        rcodeAndFlags |= (self.rcode & 0b00001111)

        bytes += struct.pack('!B', rcodeAndFlags)

        bytes += u16ToBytes(self.questionsCount)
        bytes += u16ToBytes(self.answersCount)

        bytes += u16ToBytes(self.nameServersCount)
        bytes += u16ToBytes(self.additionalsCount)

        return bytes

    @staticmethod
    def makeRefusal(id):
        self = DnsHeader()
        self.id = id
        self.qr = 1
        self.flagAA = False
        self.flagTC = False
        self.flagRA = True
        self.flagRD = True
        self.rcode = RCODE_SERVER_REFUSAL
        self.questionsCount = 1
        return self