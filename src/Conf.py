import sys

import yaml
import re
from StaticVlan import StaticVlan

class Conf:
    def __init__(self, confPath: str):
        self.confPath = confPath
        self.remaps = {}
        self.staticVlans = []

        self.__parseConf()
        self.__parseStatic()
        self.__parseAdlists()

    def __parseConf(self):
        with open(self.confPath, 'r') as file:
            yconf = yaml.load(file, Loader=yaml.FullLoader)

        self.host = yconf.get('host')
        if self.host is None:
            print('configuration error: `host` field not found')
            sys.exit(1)

        self.port = yconf.get('port')
        if self.port is None:
            print('configuration error: `port` field not found')
            sys.exit(1)

        self.static: dict = yconf.get('static')
        if self.static is None:
            print('configuration error: `static` field not found')
            sys.exit(1)

        self.rootServers = yconf.get('root-servers')
        if self.rootServers is None:
            print('configuration error: `root-servers` field not found')
            sys.exit(1)

        self.blocklists = yconf.get('blocklists')
        if self.blocklists is None:
            print('configuration error: `blocklists` field not found')
            sys.exit(1)

        self.persistentLog = yconf.get('persistent-log')
        if self.persistentLog is None:
            print('configuration error: `persistent-log` field not found')
            sys.exit(1)

        self.logging = yconf.get('logging')
        if self.logging is None:
            print('configuration error: `loggin` field not found')
            sys.exit(1)

    def __parseStatic(self):
        keys = list(self.static.keys())

        for key in keys:
            if key.startswith('_vlan'):
                self.staticVlans.append(StaticVlan(self.static.pop(key), key))

    def __parseAdlists(self):
        for filePath in self.blocklists:
            if not filePath:
                continue

            self.__parseAdlist(filePath)

    def __parseAdlist(self, filePath: str):
        with open(filePath, 'r') as file:
            content = file.read()

        for line in content.split('\n'):
            if line.strip().startswith('#') or not line:
                continue

            chunks = line.strip().split(' ')
            ip = chunks[0].strip()

            hostname = chunks[1].strip()
            hostnameRegex = r'{}'.format(hostname.replace('.', r'\.').replace('*', '.*'))

            self.remaps[hostnameRegex] = ip

    def search(self, target: str) -> str|None:
        ip = self.static.get(target)
        if ip is not None:
            return ip

        # some programs add `.localhost` when not TLD is provided
        ip = self.static.get(target.removesuffix('.localhost'))
        if ip is not None:
            return ip

        # some programs add `.local` when not TLD is provided
        ip  = self.static.get(target.removesuffix('.local'))
        if ip is not None:
            return ip

        for pattern, ip in self.remaps.items():
            if re.match(pattern, target):
                return ip