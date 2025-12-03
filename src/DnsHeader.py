from constants import RCODE_SERVER_REFUSAL, QR_BIT, OPCODE_BITS, FLAG_AA_BIT, FLAG_TC_BIT, FLAG_RD_BIT, RCODE_BITS, FLAG_RA_BIT
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

        self.qr = checkBitFlag(opcodeAndFlags, QR_BIT)
        self.opcode = opcodeAndFlags & OPCODE_BITS
        self.flagAA = checkBitFlag(opcodeAndFlags, FLAG_AA_BIT)
        self.flagTC = checkBitFlag(opcodeAndFlags, FLAG_TC_BIT)
        self.flagRD = checkBitFlag(opcodeAndFlags, FLAG_RD_BIT)

        rcodeAndFlags = bytes[index]
        index += 1

        self.flagRA = checkBitFlag(rcodeAndFlags, FLAG_RA_BIT)
        self.rcode = rcodeAndFlags & RCODE_BITS

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
        opcodeAndFlags |= QR_BIT if self.qr else 0
        opcodeAndFlags |= (self.opcode & OPCODE_BITS)
        opcodeAndFlags |= FLAG_AA_BIT if self.flagAA else 0
        opcodeAndFlags |= FLAG_TC_BIT if self.flagTC else 0
        opcodeAndFlags |= FLAG_RD_BIT if self.flagRD else 0

        bytes += struct.pack(U8, opcodeAndFlags)

        rcodeAndFlags = 0
        rcodeAndFlags |= FLAG_RA_BIT if self.flagRA else 0
        rcodeAndFlags |= (self.rcode & RCODE_BITS)

        bytes += struct.pack(U8, rcodeAndFlags)

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