from qtype import QTYPE
from validation import *
import re

class StaticRemap:
    def __init__(self, qname=None, A=None, TXT=None, AAAA=None, CNAME=None):
        self.qname = qname

        self.regexQname = None
        if '*' in self.qname:
            self.regexQname = qname.replace('.', '\\.').replace('*', '.*')

        self.validateRemap(
            remap=A, qname=qname, remapType='A', validationFn=validateIPv4
        )
        self.a = A

        self.validateRemap(
            remap=AAAA, qname=qname, remapType='AAAA', validationFn=validateIPv6
        )
        self.aaaa = AAAA

        self.validateRemap(
            remap=TXT, qname=qname, remapType='TXT', validationFn=validateTxtRecord
        )
        self.txt = TXT

        self.validateRemap(
            remap=CNAME, qname=qname, remapType='CNAME', validationFn=validateDomainName
        )
        self.cname = CNAME

    @staticmethod
    def validateRemap(remap, qname, remapType, validationFn):
        if remap is None:
            return

        if isinstance(remap, list):
            types = list(set(type(entry) for entry in remap))
            if len(types) != 1 or types[0] != str:
                raise TypeError(f'`{remapType}` record for `{qname}` must either be a string or a list of strings')

            for entry in remap:
                if not validationFn(entry):
                    raise ValueError(f'Invalid record `{entry}` [{remapType} record] for `{qname}`')

        if isinstance(remap, str):
            if not validationFn(remap):
                raise ValueError(f'Invalid record `{remap}` [{remapType} record] for `{qname}`')

        if not isinstance(remap, str) and not isinstance(remap, list):
            raise TypeError(f'`{remapType}` record for `{qname}` must either be a string or a list of strings')

    def has(self, qname, type):
        if self.regexQname is not None:
            if re.fullmatch(self.regexQname, qname) is None:
                return None

        else:
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