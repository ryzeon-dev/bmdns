from Conf import Conf
from DNS import DNS

VERSION = 'v2.0.4'

if __name__ == '__main__':
    conf = Conf('/etc/bmdns/conf.yaml')
    dns = DNS(conf)
    dns.listen()