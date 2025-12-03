import re
from constants import TXT_RECORD_MAX_LENGTH

def validateIPv4(ip):
    return re.fullmatch(
        '^((25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])\\.){3}(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])$',
        ip
    ) is not None

def validateIPv6(ip):
    return re.fullmatch(
        '^(?:(?:[a-f0-9]*)?:){1,7}[a-f0-9]*$',
        ip
    ) is not None

def validateDomainName(name):
    if re.fullmatch(
        '(?i)^[a-z0-9]\\.?([a-z0-9\\-]*\\.)*[a-z0-9\\-]+$',
        name
    ) is None:
        return False

    if 0 < len(name.removesuffix('.')) <= 253:
        return True

    return False

def validateTxtRecord(record):
    return 0 <= len(record) <= TXT_RECORD_MAX_LENGTH