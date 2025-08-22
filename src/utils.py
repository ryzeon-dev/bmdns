import struct

def bytesToU16(bytes):
    return struct.unpack('!H', bytes[0:2])[0]

def u16ToBytes(value):
    return struct.pack('!H', value)

def bytesToU32(bytes):
    return struct.unpack('!I', bytes[0:4])[0]

def u32ToBytes(value):
    return struct.pack('!I', value)

def decodeName(fullBytes, startIndex):
    index = startIndex
    chunks = []

    while ((size := fullBytes[index]) != 0):
        index += 1

        if size & 0b11000000:
            pointer = ((size & 0b00111111) << 8) | fullBytes[index]

            name = decodeName(fullBytes, pointer)
            return name

        else:
            buffer = ''

            for _ in range(size):
                buffer += chr(fullBytes[index])
                index += 1

            chunks.append(buffer)

    return '.'.join(chunks)

def checkBitFlag(byte, bitpos):
    return (byte & bitpos) == bitpos

def getNameBytes(bytes):
    index = 0
    firstSize = bytes[index]

    # 0b11000000 = 0xC0 = 192 pointer signaler in byte stream
    if firstSize & 0b11000000:
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
        bytes += struct.pack('!B', int(chunk))

    return bytes