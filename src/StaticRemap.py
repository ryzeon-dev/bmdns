from qtype import QTYPE
from validation import *

class StaticRemap:
    def __init__(self, qname=None, A=None, TXT=None, AAAA=None, CNAME=None):
        self.qname = qname

        if A is not None:
            if not isinstance(A, str):
                raise TypeError(f'`A` record for `{qname}` must be a string')

            if not validateIPv4(A):
                raise ValueError(f'Invalid IPv4 `{A}` [A record] for `{qname}`')
        self.a = A

        if AAAA is not None:
            if not isinstance(AAAA, str):
                raise TypeError(f'`AAAA` record for `{qname}` must be a string')

            if not validateIPv6(AAAA):
                raise ValueError(f'Invalid IPv6 `{AAAA}` [AAAAA record] for `{qname}`')
        self.aaaa = AAAA

        if TXT is not None:
            if isinstance(TXT, list):
                types = list(set(type(entry) for entry in TXT))
                if len(types) != 1 or types[0] != str:
                    raise TypeError(f'`TXT` record for `{qname}` must either be a string or a list of strings')

                for entry in TXT:
                    if not validateTxtRecord(entry):
                        raise ValueError(f'Invalid record `{entry}` [TXT record] for `{qname}`')

            if isinstance(TXT, str):
                if not validateTxtRecord(TXT):
                    raise ValueError(f'Invalid record `{TXT}` [TXT record] for `{qname}`')

            if not isinstance(TXT, str) and not isinstance(TXT, list):
                raise TypeError(f'`TXT` record for `{qname}` must either be a string or a list of strings')
        self.txt = TXT

        if CNAME is not None:
            if not isinstance(CNAME, str):
                raise TypeError(f'`CNAME` record for `{qname}` must be a string')
        
            if not validateDomainName(CNAME):
                raise ValueError(f'Invalid CNAME `{CNAME}` [CNAME record] for `{qname}`')
        self.cname = CNAME

    def has(self, qname, type):
        if qname != self.qname:
            return None

        if type == QTYPE.A:
            return self.a

        if type == QTYPE.AAAA:
            return self.aaaa

        if type == QTYPE.TXT:
            return self.txt

        if type == QTYPE.CNAME:
            return self.cname

        return None

    @staticmethod
    def fromYaml(domain, remap):
        if isinstance(remap, str):
            return StaticRemap(
                qname=domain,
                A=remap
            )

        if isinstance(remap, dict):
            return StaticRemap(
                qname=domain,
                A=remap.get('A'),
                AAAA=remap.get('AAAA'),
                CNAME=remap.get('CNAME'),
                TXT=remap.get('TXT')
            )

        raise TypeError(f'Static remap can either be str or dict (raised while parsing static configuration for "{domain}")')

    def __repr__(self):
        repr = f'StaticRemap( domain: {self.qname}'

        if self.a:
            repr += f' ; A: {self.a}'

        if self.aaaa:
            repr += f' ; AAAA: {self.aaaa}'

        if self.txt:
            repr += f' ; TXT: {self.txt}'

        if self.cname:
            repr += f' ; CNAME: {self.cname}'

        repr += ' )'
        return repr