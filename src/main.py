import sys
import os

from Conf import Conf
from DNS import DNS
from utils import logFatalError

VERSION = 'v5.1.0'

if __name__ == '__main__':
    if os.sys.platform == 'linux':
        CONF_PATH = '/etc/bmdns/conf.yaml'

    elif os.sys.platform == 'win32':
        programFiles = os.environ.get('PROGRAMFILES')
        CONF_PATH = os.path.join(programFiles, 'bmdns', 'conf.yaml')

    else:
        logFatalError('Fatal error: unrecognized os')
        sys.exit(1)

    try:
        conf = Conf(CONF_PATH)

    except FileNotFoundError:
        logFatalError('Fatal error: execution attempt without proper install (conf file not found)')
        sys.exit(1)

    except Exception as e:
        logFatalError(f'Fatal error: {e}')
        sys.exit(1)

    try:
        dns = DNS(conf)
        dns.listen()

    except PermissionError:
        logFatalError('Fatal error: unsufficient permissions while attempting to run')
        sys.exit(1)

    except Exception as e:
        logFatalError(f'Fatal error: {e}')
        sys.exit(1)
