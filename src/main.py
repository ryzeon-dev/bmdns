from Conf import Conf
from DNS import DNS

import sys
import os

VERSION = 'v3.2.1'

if __name__ == '__main__':
    if os.sys.platform == 'linux':
        CONF_PATH = '/etc/bmdns/conf.yaml'

    elif os.sys.platform == 'win32':
        programFiles = os.environ.get('PROGRAMFILES')
        CONF_PATH = os.path.join(programFiles, 'bmdns', 'conf.yaml')

    else:
        print('Error: unrecognized os')
        sys.exit(1)

    try:
        conf = Conf(CONF_PATH)

    except FileNotFoundError:
        print('Fatal: execution attempt without proper install (conf file not found)')
        sys.exit(1)

    except Exception as e:
        print(f'Fatal: {e}')
        sys.exit(1)

    try:
        dns = DNS(conf)
        dns.listen()

    except PermissionError:
        print('Fatal: unsufficient permissions while attempting to run')
        sys.exit(1)

    except Exception as e:
        print(f'Fatal: {e}')
        sys.exit(1)
