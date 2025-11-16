from qtype import QTYPE

class StaticRemap:
    def __init__(self, qname=None, A=None, TXT=None, AAAA=None, CNAME=None):
        self.qname = qname
        self.a = A
        self.aaaa = AAAA
        self.txt = TXT
        self.cname = CNAME

    def has(self, qname, type):
        if qname != qname:
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

        raise TypeError('Static blocklist can either be str or dict')

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