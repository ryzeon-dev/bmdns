import os.path
import sys
import yaml
import re

from StaticVlan import StaticVlan
from StaticRemap import StaticRemap
from src.utils import logFatalError
from src.validation import validateIPv4


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
            logFatalError('Fatal: `host` field not found')
            sys.exit(1)

        if not isinstance(self.host, str):
            logFatalError(f'Fatal: `host` field must be a string')
            sys.exit(1)

        if not validateIPv4(self.host):
            logFatalError(f'Fatal: `host` field must be a valid IPv4')
            sys.exit(1)

        self.port = yconf.get('port')
        if self.port is None:
            logFatalError('Fatal: `port` field not found')
            sys.exit(1)

        if not isinstance(self.port, int):
            logFatalError('Fatal: `port` field must contain an integer')
            sys.exit(1)

        if not (0 < self.port < 65536):
            logFatalError('Fatal: `port` field must be a valid port number')
            sys.exit(1)

        self.static: dict = yconf.get('static')
        if self.static is None:
            logFatalError('Fatal: `static` field not found')
            sys.exit(1)

        self.rootServers = yconf.get('root-servers')
        if self.rootServers is None:
            logFatalError('Fatal: `root-servers` field not found')
            sys.exit(1)

        if not isinstance(self.rootServers, list) or any(map(lambda e: type(e) != str, self.rootServers)):
            logFatalError(f'Fatal: `root-servers` field must contain a list of strings')
            sys.exit(1)

        if any(map(lambda e: not validateIPv4(e), self.rootServers)):
            logFatalError(f'Fatal: `root-servers` field must contain a list of valid IPv4 addresses')
            sys.exit(1)

        self.blocklists = yconf.get('blocklists')
        if self.blocklists is None:
            logFatalError('Fatal: `blocklists` field not found')
            sys.exit(1)

        if not isinstance(self.blocklists, list) or any(map(lambda e: type(e) != str, self.blocklists)):
            logFatalError(f'Fatal: `blocklists` field must contain a list of strings')
            sys.exit(1)

        self.persistentLog = yconf.get('persistent-log')
        if self.persistentLog is None:
            logFatalError('Fatal: `persistent-log` field not found')
            sys.exit(1)

        if not isinstance(self.persistentLog, bool):
            logFatalError('Fatal: `persistent-log` field must contain a bool')
            sys.exit(1)

        # if no preference is specified (most probably due to an old configuration file), logging is asserted as true
        self.logging = yconf.get('logging')
        if self.logging is None:
            self.logging = True

        if not isinstance(self.logging, bool):
            logFatalError('Fatal: `logging` field must contain a bool')
            sys.exit(1)

        # if no preference is specified (most probably due to an old configuration file), colored logging is asserted as true
        self.colorLog = yconf.get('color-log')
        if self.colorLog is None:
            self.colorLog = True

        if not isinstance(self.colorLog, bool):
            logFatalError('Fatal: `color-log` field must contain a bool')
            sys.exit(1)

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

            if not os.path.exists(filePath):
                logFatalError(f'Fatal: `{filePath}` blocklist file not found')
                sys.exit(1)

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