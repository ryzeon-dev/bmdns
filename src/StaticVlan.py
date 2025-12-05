import sys

from StaticRemap import StaticRemap
from src.utils import logFatalError
from src.validation import validateIPv4, validateVlanMask


def ipToU32(ip):
    chunks = ip.split('.')
    multiplier = 3

    intip = 0
    for chunk in chunks:
        intip |= int(chunk) << (8 * multiplier)
        multiplier -= 1

    return intip

def u32ToIp(intip):
    return f'{(intip >> 24) & 0xFF}.{(intip >> 16) & 0xFF}.{(intip >> 8) & 0xFF}.{intip & 0xFF}'

def maskFromCidr(cidr):
    netBits = cidr
    hostBits = 32 - cidr

    intNetmask = 0
    for i in range(netBits):
        intNetmask |= 1 << i

    intNetmask <<= hostBits
    return intNetmask

class StaticVlan:
    def __init__(self, conf: dict, name: str):
        self.name = name

        if '__vlanmask' not in conf:
            logFatalError(f'Fatal: `__vlanmask` not specified in `{name}` static vlan mapping')
            sys.exit(1)

        self.vlanMask = conf.pop('__vlanmask')
        if not isinstance(self.vlanMask, str):
            logFatalError(f'Fatal: `__vlanmask` field must contain a string (from `{name}` vlan configuration)')
            sys.exit(1)

        if not validateVlanMask(self.vlanMask):
            logFatalError(f'Fatal: invalid `__vlanmask` for vlan `{name}`')
            sys.exit(1)

        if '__block-external' in conf:
            self.blockExternal = conf.pop('__block-external')

            if not isinstance(self.blockExternal, bool):
                logFatalError(f'Fatal: `__block-external` field must contain a bool (from `{self.name}` vlan configuration)')
                sys.exit(1)

        else:
            self.blockExternal = False

        if '__exclude' in conf:
            exclude = conf.pop('__exclude')

            if isinstance(exclude, list):
                if any(map(lambda e: type(e) != str, exclude)):
                    logFatalError(f'Fatal: `__exclude` field can only contain a string or a list of strings (from `{self.name}` vlan exclusions)')
                    sys.exit(1)
                self.exclude = exclude

            elif isinstance(exclude, str):
                self.exclude = [exclude]

            else:
                logFatalError(f'Fatal: `__exclude` field can only contain a string or a list of strings (from `{self.name}` vlan exclusions)')
                sys.exit(1)

            self.exclude = exclude
            self.__parseExclusions()
        else:
            self.exclude = set()

        self.__unpackVlanMask()

        self.yamlRemaps = conf
        self.remaps = {}
        self.wildcardRemaps = []
        self.__parseRemaps()

    def __parseRemaps(self):
        for key, value in self.yamlRemaps.items():
            remap = StaticRemap.fromYaml(key, value)

            if remap.regexQname is not None:
                self.wildcardRemaps.append(remap)
            else:
                self.remaps[key] = remap

    def __unpackVlanMask(self):
        self.cidr = 24

        if '/' in self.vlanMask:
            chunks = self.vlanMask.split('/')
            ip = chunks[0]
            self.cidr = int(chunks[1])

        else:
            ip = self.vlanMask

        self.u32NetMask = maskFromCidr(self.cidr)
        self.u32BaseIp = ipToU32(ip) & self.u32NetMask
        self.u32BrdIp = (self.u32BaseIp | (~self.u32NetMask)) & 0xFFFFFFFF

    def __parseExclusions(self):
        u32Exclude = set()

        for exclusion in self.exclude:
            if not validateIPv4(exclusion):
                logFatalError(f'Fatal: `{exclusion}` is not a valid IPv4 (from `{self.name}` vlan exclusions)')
                sys.exit(1)

            u32Exclude.add(ipToU32(exclusion))
        self.exclude = u32Exclude

    def allows(self, ip):
        u32Ip = ipToU32(ip)
        return self.u32BaseIp < u32Ip < self.u32BrdIp and u32Ip not in self.exclude

    def search(self, target, qtype):
        remap = self.remaps.get(target)
        if remap is not None:
            return remap.has(target, qtype)

        # some programs add `.localhost` when not TLD is provided
        remap = self.remaps.get(target.removesuffix('.localhost'))
        if remap is not None:
            return remap.has(target, qtype)

        # some programs add `.local` when not TLD is provided
        remap = self.yamlRemaps.get(target.removesuffix('.local'))
        if remap is not None:
            return remap.has(target, qtype)

        # searches for wildcard remaps
        for wildcard in self.wildcardRemaps:
            if remap := wildcard.has(target, qtype):
                return remap