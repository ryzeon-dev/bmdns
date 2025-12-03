import struct
import time
import os
from constants import LOG_DIR, U8, U16, U32, QNAME_POINTER_FLAG, QNAME_REVERSE_POINTER_FLAG

def bytesToU16(bytes):
    return struct.unpack(U16, bytes[0:2])[0]

def u16ToBytes(value):
    return struct.pack(U16, value)

def bytesToU32(bytes):
    return struct.unpack(U16, bytes[0:4])[0]

def u32ToBytes(value):
    return struct.pack(U32, value)

def decodeName(fullBytes, startIndex):
    index = startIndex
    chunks = []

    while ((size := fullBytes[index]) != 0):
        index += 1

        if size & QNAME_POINTER_FLAG:
            pointer = ((size & QNAME_REVERSE_POINTER_FLAG) << 8) | fullBytes[index]

            name = decodeName(fullBytes, pointer)
            return name

        else:
            buffer = ''

            for _ in range(size):
                buffer += chr(fullBytes[index])
                index += 1

            chunks.append(buffer)

    return '.'.join(chunks)

def encodeName(name):
    splitName = name.split('.')
    encoded = b''

    for chunk in splitName:
        encoded += struct.pack(U8, len(chunk))
        encoded += chunk.encode()

    encoded += b'\x00'
    return encoded

def checkBitFlag(byte, bitpos):
    return (byte & bitpos) == bitpos

def getNameBytes(bytes):
    index = 0
    firstSize = bytes[index]

    # 0b11000000 = 0xC0 = 192 pointer signaler in byte stream
    if firstSize & QNAME_POINTER_FLAG:
        name = bytes[index:index + 2]

    else:
        nameLength = 0
        while bytes[index + nameLength] != 0:
            nameLength += 1
        nameLength += 1

        name = bytes[index:index + nameLength]

    return name

def ipToBytes(ip):
    bytes = b''

    for chunk in ip.split('.'):
        bytes += struct.pack(U8, int(chunk))

    return bytes

def ipv6ToBytes(ip):
    bytes = b''
    chunks = ip.split(':')

    if '' in chunks:
        index = chunks.index('')
        chunks.remove('')

        for _ in range(8 - len(chunks)):
            chunks.insert(index, '0')

    for chunk in chunks:
        u16Chunk = int(chunk, 16)
        bytes += u16ToBytes(u16Chunk)

    return bytes

def fmtNow():
    now = time.localtime()
    return f'{now.tm_year}/{now.tm_mon}/{now.tm_mday} {now.tm_hour}:{now.tm_min}:{now.tm_sec}'

def logFatalError(text):
    now = fmtNow()

    with open(os.path.join(LOG_DIR, 'bmdns_error.log'), 'w') as file:
        file.write(f'{now} | {text}')