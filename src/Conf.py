import sys
import yaml
import re

from StaticVlan import StaticVlan
from StaticRemap import StaticRemap

class Conf:
    def __init__(self, confPath: str):
        self.confPath = confPath
        self.blocklist = {}
        self.remaps = {}
        self.wildcardRemaps = []
        self.staticVlans = []

        self.__parseConf()
        self.__parseStatic()
        self.__parseBlocklists()

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

        # if no preference is specified (most probably due to an old configuration file), logging is asserted as true
        self.logging = yconf.get('logging')
        if self.logging is None:
            self.logging = True

        # if no preference is specified (most probably due to an old configuration file), colored logging is asserted as true
        self.colorLog = yconf.get('color-log')
        if self.colorLog is None:
            self.colorLog = True

    def __parseStatic(self):
        keys = list(self.static.keys())

        for key in keys:
            if key.startswith('_vlan'):
                self.staticVlans.append(StaticVlan(self.static.pop(key), key))

            else:
                remap = StaticRemap.fromYaml(key, self.static.pop(key))

                if remap.regexQname is not None:
                    self.wildcardRemaps.append(remap)

                else:
                    self.remaps[key] = remap

    def __parseBlocklists(self):
        for filePath in self.blocklists:
            if not filePath:
                continue

            self.__parseBlocklistFile(filePath)

    def __parseBlocklistFile(self, filePath: str):
        with open(filePath, 'r') as file:
            content = file.read()

        for line in content.split('\n'):
            if line.strip().startswith('#') or not line:
                continue

            chunks = line.strip().split(' ')
            ip = chunks[0].strip()

            hostname = chunks[1].strip()
            hostnameRegex = r'{}'.format(hostname.replace('.', r'\.').replace('*', '.*'))

            self.blocklist[hostnameRegex] = ip

    def search(self, target: str, qtype: int) -> str|None:
        remap = self.remaps.get(target)
        if remap is not None:
            return remap.has(target, qtype)

        # some programs add `.localhost` when not TLD is provided
        remap = self.remaps.get(target.removesuffix('.localhost'))
        if remap is not None:
            return remap.has(target, qtype)

        # some programs add `.local` when not TLD is provided
        remap  = self.remaps.get(target.removesuffix('.local'))
        if remap is not None:
            return remap.has(target, qtype)

        # searches for wildcard remaps
        for wildcard in self.wildcardRemaps:
            if remap := wildcard.has(target, qtype):
                return remap

        for pattern, ip in self.blocklist.items():
            if re.match(pattern, target):
                return ip