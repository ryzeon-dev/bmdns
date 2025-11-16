import sys
import re
from StaticRemap import StaticRemap

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
            print(f'`__vlanmask` not specified in `{name}` static vlan mapping', file=sys.stderr)
            sys.exit(1)

        self.vlanMask = conf.pop('__vlanmask')

        if '__block-external' in conf:
            self.blockExternal = conf.pop('__block-external')
        else:
            self.blockExternal = False

        self.__unpackVlanMask()

        self.yamlRemaps = conf
        self.remaps = {}
        self.__parseRemaps()

    def __parseRemaps(self):
        for key, value in self.yamlRemaps.items():
            self.remaps[key] = StaticRemap(key, value)

    def __unpackVlanMask(self):
        ip = None
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

    def allows(self, ip):
        u32Ip = ipToU32(ip)
        return self.u32BaseIp < u32Ip < self.u32BrdIp

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
