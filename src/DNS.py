import socket as sk
from _thread import start_new_thread
from Cache import Cache

from DnsHeader import DnsHeader
from DnsQuestion import DnsQuestion
from DnsRecord import DnsRecord
from utils import ipToBytes, u16ToBytes, decodeName
from Logger import Logger

class DNS:
    def __init__(self, conf):
        self.conf = conf

        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        try:
            self.socket.bind((conf.host, conf.port))
        except:
            raise Exception(f'Cannot bind address "{self.conf.host}:{self.conf.port}"')

        self.cache = Cache()
        self.logger = Logger()

    def listen(self):
        while True:
            bytes, clientAddress = self.socket.recvfrom(2048)
            start_new_thread(self.handler, (bytes, clientAddress))

    def handler(self, bytes, clientAddress):
        header = DnsHeader.fromBytes(bytes)
        question = DnsQuestion.fromBytes(bytes[12:])

        requestId = header.id
        qname = decodeName(question.qname, 0)

        strRequestId = str(requestId).ljust(5)
        fmtClientAddress = f'{clientAddress[0]}:{clientAddress[1]}'

        self.logger.alert(f'{strRequestId} | {fmtClientAddress} asks for {qname}')

        if responseBytes := self.cache.getFotId(qname, requestId):
            self.loggerl.log(f'{strRequestId} | giving cached answer to {fmtClientAddress} asking for {qname}')
            try:
                self.socket.sendto(responseBytes, clientAddress)
            except:
                self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

            return

        if ip := self.conf.search(qname):
            self.logger.log(f'{strRequestId} | giving static answer "{ip}" to {fmtClientAddress} asking for {qname}')
            answer = DnsRecord()

            answer.name = b'\xc0\x0c'
            answer.type = question.qtype

            answer.class_ = question.qclass
            answer.ttl = 65536

            answer.dataSize = 4
            answer.data = ipToBytes(ip)

            header.answersCount = 1
            header.qr = 1
            responseBytes = b''

            responseBytes += header.toBytes()
            responseBytes += question.toBytes()
            responseBytes += answer.toBytes()

            try:
                self.socket.sendto(responseBytes, clientAddress)
            except:
                self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

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

            self.cache.append(responseBytes)
            return

        self.logger.error(f'{strRequestId} | giving no answer to {fmtClientAddress} asking for {qname}')

    def askRootServer(self, server, questionBytes):
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.settimeout(1)

        try:
            sock.sendto(questionBytes, (server, 53))

        except:
            self.logger.error(f'Error: could not reach "{server}" root server')
            return

        try:
            responseBytes, address = sock.recvfrom(2048)

        except:
            return None

        return responseBytes