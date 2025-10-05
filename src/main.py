from Conf import Conf
from DNS import DNS

import sys
import os

VERSION = 'v2.1.0'

if __name__ == '__main__':
    if os.sys.platform == 'linux':
        conf = Conf('/etc/bmdns/conf.yaml')

    elif os.sys.platform == 'win32':
        programFiles = os.environ.get('PROGRAMFILES(X86)')
        conf = Conf(os.path.join(programFiles, 'bmdns', 'conf.yaml'))

    else:
        print('Error: unrecognized os')
        sys.exit(1)

    dns = DNS(conf)
    dns.listen()