import socket as sk
from _thread import start_new_thread

from Cache import Cache
from DnsHeader import DnsHeader
from DnsQuestion import DnsQuestion
from DnsRecord import DnsRecord
from utils import ipToBytes, u16ToBytes, decodeName
from Logger import Logger
from constants import *

class DNS:
    def __init__(self, conf):
        self.conf = conf
        self.logger = Logger(self.conf.persistentLog)

        self.useStaticVlans = self.conf.staticVlans != []

        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        try:
            self.socket.bind((conf.host, conf.port))

        except:
            raise Exception(f'Cannot bind address "{self.conf.host}:{self.conf.port}"')

        self.cache = Cache()
        self.cnameCache = Cache()

    def listen(self):
        while True:
            bytes, clientAddress = self.socket.recvfrom(RECV_SIZE)
            start_new_thread(self.handler, (bytes, clientAddress))

    def handler(self, bytes, clientAddress):
        header = DnsHeader.fromBytes(bytes)
        question = DnsQuestion.fromBytes(bytes[HEADER_BYTE_SIZE:])

        def assembleResponse(ip):
            answer = DnsRecord()

            # [0xC0, 0x0C] = [192, 12] is the standard pointer for referencing the qname in the question
            answer.name = QNAME_STD_POINTER  #
            answer.type = QUESTIONTYPE_A

            answer.class_ = question.qclass
            answer.ttl = RECORD_MAX_TTL

            answer.dataSize = IP_ADDRESS_BYTE_SIZE
            answer.data = ipToBytes(ip)

            header.questionsCount = 1
            header.nameServersCount = 0
            header.additionalsCount = 0

            # only one response for statically assigned addresses
            header.answersCount = 1
            header.qr = QR_RESPONSE
            header.flagRA = True # required by some clients

            responseBytes = b''
            responseBytes += header.toBytes()
            responseBytes += question.toBytes()
            responseBytes += answer.toBytes()

            return responseBytes

        clientIp = clientAddress[0]
        requestId = header.id

        qname = decodeName(question.qname, 0)
        qtype = question.qtype

        # logging variables
        strRequestId = str(requestId).ljust(5)
        fmtClientAddress = f'{clientAddress[0]}:{clientAddress[1]}'

        self.logger.alert(f'{strRequestId} | {fmtClientAddress} asks for {qname}')

        # BMDNS does not allow IPv6 queries
        if qtype == QUESTIONTYPE_AAAA: # AAAA -> IPv6 query
            errorHeader = DnsHeader()
            errorHeader.id = header.id

            errorHeader.qr = QR_RESPONSE
            # indicates refusal to answer from DNS server
            errorHeader.rcode = RCODE_SERVER_REFUSAL

            try:
                self.socket.sendto(errorHeader.toBytes(), clientAddress)

            except:
                pass

            self.logger.error(f'{strRequestId} | {fmtClientAddress} asked for IPv6 query: refusing')
            return

        if qtype == QUESTIONTYPE_A: # A -> IPv4 query
            if self.useStaticVlans:
                for staticVlan in self.conf.staticVlans:
                    # checks if the client IP address belongs to a registered vlan
                    if not staticVlan.allows(clientIp):
                        continue

                    if ip := staticVlan.search(qname):
                        self.logger.log(f'{strRequestId} | giving static vlan `{staticVlan.name}` answer "{ip}" to {fmtClientAddress} asking for {qname}')
                        responseBytes = assembleResponse(ip)

                        try:
                            self.socket.sendto(responseBytes, clientAddress)

                        except:
                            self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

                        return

            if ip := self.conf.search(qname):
                self.logger.log(f'{strRequestId} | giving static answer "{ip}" to {fmtClientAddress} asking for {qname}')
                responseBytes = assembleResponse(ip)

                try:
                    self.socket.sendto(responseBytes, clientAddress)

                except:
                    self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

                # # response gets cached even if socket answer fails
                # self.cache.append(responseBytes)
                return

            if responseBytes := self.cache.getForId(qname, requestId):
                self.logger.log(f'{strRequestId} | giving cached answer to {fmtClientAddress} asking for {qname}')

                try:
                    self.socket.sendto(responseBytes, clientAddress)

                except:
                    self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

                return

        elif qtype == QUESTIONTYPE_CNAME:
            if responseBytes := self.cnameCache.getForId(qname, requestId):
                self.logger.log(f'{strRequestId} | giving cached CNAME to {fmtClientAddress} asking for {qname}')

                try:
                    self.socket.sendto(responseBytes, clientAddress)

                except:
                    self.logger.error(f'{strRequestId} | Error: cannot send cname response to {fmtClientAddress}')

                return

        for server in self.conf.rootServers:
            responseBytes = self.askRootServer(server, bytes)

            if responseBytes is None:
                continue

            self.logger.log(f'{strRequestId} | giving root server answer to {fmtClientAddress} asking for {qname}')
            responseBytes = u16ToBytes(requestId) + responseBytes[2:]

            try:
                self.socket.sendto(responseBytes, clientAddress)

            except:
                self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

            if qtype == QUESTIONTYPE_A:
                self.cache.append(responseBytes)

            elif qtype == QUESTIONTYPE_CNAME:
                self.cnameCache.append(responseBytes)

            return

        # extreme condition, has low probability of happening, in case a non-existent domain is queried
        self.logger.error(f'{strRequestId} | giving no answer to {fmtClientAddress} asking for {qname}')

    def askRootServer(self, server, questionBytes):
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.settimeout(1)

        # the client's request is directlty forwarded to the root server
        try:
            sock.sendto(questionBytes, (server, STD_DNS_PORT))

        except:
            self.logger.error(f'Error: could not reach "{server}" root server')
            return

        try:
            responseBytes, address = sock.recvfrom(RECV_SIZE)

        except:
            return None

        return responseBytes