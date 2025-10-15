import os

if os.sys.platform == 'linux':
    LOG_DIR = '/var/log/bmdns'
    LOG_FILE = '/var/log/bmdns/bmdns.log'

elif os.sys.platform == 'win32':
    programFiles = os.environ.get('PROGRAMFILES(X86)')
    LOG_DIR = os.path.join(programFiles, 'bmdns', 'log')
    LOG_FILE = os.path.join(LOG_DIR, 'bmdns.log')

CACHE_FLUSH_TIMEOUT = 120

QUESTIONTYPE_A = 1
QUESTIONTYPE_CNAME = 5
QUESTIONTYPE_AAAA = 28

RECORD_MAX_TTL = (2 ** 32) - 1

RCODE_SERVER_REFUSAL = 5

HEADER_BYTE_SIZE = 12

RECV_SIZE = 2048

STD_DNS_PORT = 53

QNAME_STD_POINTER = b'\xc0\x0c'

IP_ADDRESS_BYTE_SIZE = 4

QR_QUESTION = 0
QR_RESPONSE = 1