import random
import socket as sk
from _thread import start_new_thread
import ssl

from Cache import Cache
from DnsHeader import DnsHeader
from DnsQuestion import DnsQuestion
from DnsRecord import DnsRecord
from utils import u16ToBytes, decodeName
from Logger import Logger
from constants import *
from qtype import QTYPE

class DNS:
    def __init__(self, conf):
        self.conf = conf
        self.logger = Logger(self.conf.persistentLog, self.conf.logging, self.conf.colorLog)

        self.useStaticVlans = self.conf.staticVlans != []

        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)

        try:
            self.socket.bind((conf.host, conf.port))

        except:
            raise Exception(f'Cannot bind address "{self.conf.host}:{self.conf.port}"')

        self.caches = {}
        self.qtypes = QTYPE.getAll()
        self.__makeCaches()

    def __makeCaches(self):
        for qtype in self.qtypes:
            self.caches[qtype] = Cache(qtype)

    def listen(self):
        while True:
            bytes, clientAddress = self.socket.recvfrom(RECV_SIZE)
            start_new_thread(self.handler, (bytes, clientAddress))

    def handler(self, bytes, clientAddress):
        header = DnsHeader.fromBytes(bytes)
        question = DnsQuestion.fromBytes(bytes[HEADER_BYTE_SIZE:])

        clientIp = clientAddress[0]
        requestId = header.id

        qname = decodeName(question.qname, 0)
        qtype = question.qtype

        # logging variables
        strRequestId = str(requestId).ljust(5)
        fmtClientAddress = f'{clientAddress[0]}:{clientAddress[1]}'

        self.logger.alert(f'{strRequestId} | {fmtClientAddress} asks for {qname} [{QTYPE.codeToName(qtype)}]')

        def assembleResponse(data, type=QTYPE.A):
            header.questionsCount = 1
            header.nameServersCount = 0
            header.additionalsCount = 0

            header.answersCount = 1
            header.qr = QR_RESPONSE
            header.flagRA = True  # required by some clients

            answerBytes = b''
            if isinstance(data, list):
                # in presence of multiple records of the same type, randomization has to be implemented
                data = data.copy()
                random.shuffle(data)

                header.answersCount = len(data)

                for record in data:
                    dnsRecord = DnsRecord.makeFor(
                        qtype=type, qclass=question.qclass, data=record
                    )
                    answerBytes += dnsRecord.toBytes()

            else:
                answer = DnsRecord.makeFor(
                    qtype=type, qclass=question.qclass, data=data
                )
                answerBytes = answer.toBytes()

            responseBytes = b''
            responseBytes += header.toBytes()
            responseBytes += question.toBytes()
            responseBytes += answerBytes

            return responseBytes

        if self.useStaticVlans:
            for staticVlan in self.conf.staticVlans:
                # checks if the client IP address belongs to a registered vlan
                if not staticVlan.allows(clientIp):
                    continue

                # searches for the domain and qtype in the vlan configuration
                if (target := staticVlan.search(qname, qtype)):
                    self.logger.log(f'{strRequestId} | giving static vlan `{staticVlan.name}` answer "{target}" to {fmtClientAddress} asking for {qname} [{QTYPE.codeToName(qtype)}]')
                    responseBytes = assembleResponse(target, qtype)

                    try:
                        self.socket.sendto(responseBytes, clientAddress)

                    except:
                        self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

                    return

                else:
                    # if the vlan is configured to lock external access, server refusal is sent back
                    if staticVlan.blockExternal:
                        responseHeader = DnsHeader.makeRefusal(header.id)

                        responseBytes = responseHeader.toBytes()
                        responseBytes += question.toBytes()

                        self.socket.sendto(responseBytes, clientAddress)
                        self.logger.log(f'{strRequestId} | blocking external access from vlan `{staticVlan.name}` to {fmtClientAddress} asking for {qname} [{QTYPE.codeToName(qtype)}] ')
                        return

        # searches for a static remap
        if (target := self.conf.search(qname, qtype)):
            self.logger.log(f'{strRequestId} | giving static answer "{target}" to {fmtClientAddress} asking for {qname} [{qtype}]')
            responseBytes = assembleResponse(target, qtype)

            try:
                self.socket.sendto(responseBytes, clientAddress)

            except:
                self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

            return

        print(self.caches)
        # searches in cache
        if qtype in self.qtypes:
            if responseBytes := self.caches[qtype].getForId(qname, requestId):
                self.logger.log(f'{strRequestId} | giving cached {QTYPE.codeToName(qtype)} answer to {fmtClientAddress} asking for {qname}')

                try:
                    self.socket.sendto(responseBytes, clientAddress)

                except:
                    self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

                return

        # asks configured root servers
        for server in self.conf.rootServers:
            if server.startswith('tls://'):
                print('tls server detected')
                responseBytes = self.askTlsRootServer(server, bytes)

            else:
                responseBytes = self.askRootServer(server, bytes)

            if responseBytes is None:
                continue

            self.logger.log(f'{strRequestId} | giving root server answer to {fmtClientAddress} asking for {qname} [{QTYPE.codeToName(qtype)}]')
            responseBytes = u16ToBytes(requestId) + responseBytes[2:]

            try:
                self.socket.sendto(responseBytes, clientAddress)

            except:
                self.logger.error(f'{strRequestId} | Error: cannot send response to {fmtClientAddress}')

            print(f'{qtype = } ; {qtype in self.qtypes = }')
            if qtype in self.qtypes:
                self.caches[qtype].append(responseBytes)

            return

        # extreme condition, has low probability of happening, in case a non-existent domain is queried
        self.logger.error(f'{strRequestId} | giving no answer to {fmtClientAddress} asking for {qname} [{QTYPE.codeToName(qtype)}]')

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

    def askTlsRootServer(self, server, questionBytes):
        sslContext = ssl.create_default_context()
        targetServer = server.removeprefix('tls://')
        print(f'{targetServer = }')

        try:
            with sk.create_connection((targetServer, STD_DoT_PORT), timeout=5) as sock:
                with sslContext.wrap_socket(sock, server_hostname=targetServer) as tlsSocket:
                    querySize = len(questionBytes).to_bytes(2, 'big')
                    tlsSocket.sendall(querySize + questionBytes)

                    responseLength = int.from_bytes(tlsSocket.recv(2), 'big')
                    responseBytes = tlsSocket.recv(responseLength)

        except Exception as e:
            print(e)
            return

        return responseBytes