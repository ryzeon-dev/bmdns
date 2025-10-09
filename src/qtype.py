class QTYPE:
    A = 1           # IPv4
    NS = 2          # Name Server
    CNAME = 5       # Canonical Name
    SOA = 6         # Start Of Authority
    MX = 15         # Mail Exchange
    TXT = 16        # Text
    AAAA = 28       # IPv6
    DNAME = 39      # Delegation Name
    HTTPS = 65      # HTTPS Binding
    URI = 256       # Uniform Resource Idenfier
    CAA = 257       # Certification Authority Authorization

    @staticmethod
    def getAll():
        qtpyes = set()

        for attr, value in QTYPE.__dict__.items():
            if attr == attr.upper():
                qtpyes.add(value)

        return qtpyes

    @staticmethod
    def codeToName(code):
        for attr, value in QTYPE.__dict__.items():
            if value == code:
                return attr

        return None