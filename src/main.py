from Conf import Conf
from DNS import DNS

if __name__ == '__main__':
    conf = Conf('/etc/bmdns/conf.yaml')
    dns = DNS(conf)

    dns.listen()