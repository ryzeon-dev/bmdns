import os

if os.sys.platform == 'linux':
    LOG_DIR = '/var/log/bmdns'
    LOG_FILE = '/var/log/bmdns/bmdns.log'

elif os.sys.platform == 'win32':
    programFiles = os.environ.get('PROGRAMFILES')
    LOG_DIR = os.path.join(programFiles, 'bmdns', 'log')
    LOG_FILE = os.path.join(LOG_DIR, 'bmdns.log')

CACHE_FLUSH_TIMEOUT = 120

RECORD_MAX_TTL = (2 ** 32) - 1

RCODE_SERVER_REFUSAL = 5

HEADER_BYTE_SIZE = 12

RECV_SIZE = 2048

STD_DNS_PORT = 53

QNAME_STD_POINTER = b'\xc0\x0c'
QNAME_POINTER_FLAG = 0b11000000
QNAME_REVERSE_POINTER_FLAG = 0b00111111

IPv4_ADDRESS_BYTE_SIZE = 4
IPv6_ADDRESS_BYTE_SIZE = 16

QR_QUESTION = 0
QR_RESPONSE = 1

TXT_RECORD_MAX_LENGTH = 255

### ALIASES FOR STRUCT ###

U8 = '!B'
U16 = '!H'
U32 = '!I'

### DNS HEADER BITS ###

QR_BIT = 0b10000000
OPCODE_BITS = 0b01111000
FLAG_AA_BIT = 0b00000100
FLAG_TC_BIT = 0b00000010
FLAG_RD_BIT = 0b00000001
FLAG_RA_BIT = 0b10000000
RCODE_BITS = 0b00001111