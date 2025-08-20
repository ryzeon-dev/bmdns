import socket as sk
from _thread import start_new_thread
from Cache import Cache

from DnsHeader import DnsHeader
from DnsQuestion import DnsQuestion
from DnsRecord import DnsRecord
from utils import ipToBytes, u16ToBytes, decodeName


class DNS:
    def __init__(self, conf):
        self.conf = conf

        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        self.socket.bind((conf.host, conf.port))
        self.cache = Cache()

    def listen(self):
        while True:
            bytes, clientAddress = self.socket.recvfrom(2048)
            start_new_thread(self.handler, (bytes, clientAddress))

    def handler(self, bytes, clientAddress):
        header = DnsHeader.fromBytes(bytes)
        question = DnsQuestion.fromBytes(bytes[12:])

        requestId = header.id
        strRequestId = str(requestId).ljust(5
                                            )
        qname = decodeName(question.qname, 0)

        print(f'[!] {strRequestId} | {clientAddress} asks for {qname}')

        if responseBytes := self.cache.getFotId(qname, requestId):
            print(f'[*] {strRequestId} | giving cached answer to {clientAddress} asking for {qname}')
            self.socket.sendto(responseBytes, clientAddress)
            return

        if ip := self.conf.search(qname):
            print(f'[*] {strRequestId} | giving static answer "{ip}" to {clientAddress} asking for {qname}')
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

            self.socket.sendto(responseBytes, clientAddress)
            return

        for server in self.conf.rootServers:
            responseBytes = self.askRootServer(server, bytes)

            if responseBytes is None:
                continue

            print(f'[*] {strRequestId} | giving root server answer to {clientAddress} asking for {qname}')

            responseBytes = u16ToBytes(requestId) + responseBytes[2:]
            self.socket.sendto(responseBytes, clientAddress)
            self.cache.append(responseBytes)
            return

        print(f'[x] {strRequestId} | giving no answer to {clientAddress} asking for {qname}')

    def askRootServer(self, server, questionBytes):
        sock = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        sock.settimeout(1)

        sock.sendto(questionBytes, (server, 53))
        try:
            responseBytes, address = sock.recvfrom(2048)

        except:
            return None

        return responseBytes