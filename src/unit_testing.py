import unittest
import tempfile

from StaticRemap import StaticRemap
from qtype import QTYPE
from StaticVlan import StaticVlan
from Conf import Conf
from src.utils import checkBitFlag, ipToBytes, ipv6ToBytes
from utils import encodeName, decodeName
from validation import *

##########################
### STATIC REMAP TESTS ###
##########################

class StaticRemapTest(unittest.TestCase):
    def test_A_only_success(self):
        qname = 'qname'
        ip = '192.168.1.1'

        remap = StaticRemap(qname=qname, A=ip)
        self.assertIsNotNone(remap.has(qname=qname, type=QTYPE.A))
        self.assertIsNone(remap.has(qname=qname, type=QTYPE.TXT))
        self.assertIsNone(remap.has(qname='wrong_qname', type=QTYPE.A))

    def test_A_only_fail_wrong_ip(self):
        qname = 'qname'
        ip = '192.168.1.256'

        try:
            StaticRemap(qname=qname, A=ip)

        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))

        else:
            self.fail('No exception raised')

    def test_A_only_fail_wrong_type(self):
        qname = 'qname'
        ip = 0

        try:
            StaticRemap(qname=qname, A=ip)

        except Exception as e:
            self.assertTrue(isinstance(e, TypeError))

        else:
            self.fail('No exception raised')

    def test_A_only_list_success(self):
        qname = 'qname'
        A = ['192.168.1.1', '10.0.0.1']

        remap = StaticRemap(qname=qname, A=A)
        self.assertEqual(remap.has(qname, QTYPE.A), A)

    def test_multi_type_success(self):
        qname = 'qname'
        A = '192.168.1.1'
        TXT = 'txt record'
        AAAA = 'ffee:beef::deeb'
        CNAME = 'qname.local'

        remap = StaticRemap(
            qname=qname, A=A, AAAA=AAAA, TXT=TXT, CNAME=CNAME
        )

        self.assertIsNotNone(remap.has(qname, QTYPE.A))
        self.assertIsNotNone(remap.has(qname, QTYPE.AAAA))
        self.assertIsNotNone(remap.has(qname, QTYPE.TXT))
        self.assertIsNotNone(remap.has(qname, QTYPE.CNAME))

    def test_multi_type_fail_wrong_type(self):
        qname = 'qname'
        A = '192.168.1.1'
        TXT = 'txt record'
        AAAA = 0xFF
        CNAME = 'qname.local'

        try:
            StaticRemap(
                qname=qname, A=A, AAAA=AAAA, TXT=TXT, CNAME=CNAME
            )
        except Exception as e:
            self.assertTrue(isinstance(e, TypeError))

        else:
            self.fail('test should have raised exception')

    def test_multi_type_fail_wrong_value(self):
        qname = 'qname'
        A = '192.168.1.1'
        TXT = 'txt record'
        AAAA = 'this is not ipv6'
        CNAME = 'qname.local'

        try:
            StaticRemap(
                qname=qname, A=A, AAAA=AAAA, TXT=TXT, CNAME=CNAME
            )
        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))

        else:
            self.fail('test should have raised exception')

    def test_multi_type_lists_success(self):
        qname = 'qname'
        A = ['192.168.1.1', '10.0.0.1']
        TXT = ['txt record', 'another txt record']
        AAAA = ['ffee:beef::deeb', 'ffee:deeb::beef']
        CNAME = ['qname.local', 'qname.lan']

        remap = StaticRemap(
            qname=qname, A=A, AAAA=AAAA, TXT=TXT, CNAME=CNAME
        )

        self.assertEqual(remap.has(qname, QTYPE.A), A)
        self.assertEqual(remap.has(qname, QTYPE.AAAA), AAAA)
        self.assertEqual(remap.has(qname, QTYPE.TXT), TXT)
        self.assertEqual(remap.has(qname, QTYPE.CNAME), CNAME)

    def test_multi_type_lists_fail_txt_too_long(self):
        qname = 'qname'
        A = ['192.168.1.1', '10.0.0.1']
        TXT = ['txt record', 'another txt record', 'a'*300]
        AAAA = ['ffee:beef::deeb', 'ffee:deeb::beef']
        CNAME = ['qname.local', 'qname.lan']

        try:
            StaticRemap(
                qname=qname, A=A, AAAA=AAAA, TXT=TXT, CNAME=CNAME
            )

        except Exception as e:
            self.assertTrue(isinstance(e, ValueError))

        else:
            self.fail('test should have raised exception')

    def test_stating_wildcard_remap_success(self):
        wildcardQname = '*local.lan'
        A = '192.168.0.2'

        remap = StaticRemap(qname=wildcardQname, A=A)

        self.assertEqual(remap.has(qname='machine.local.lan', type=QTYPE.A), A)
        self.assertEqual(remap.has(qname='local.lan', type=QTYPE.A), A)

    def test_stating_wildcard_remap_fail(self):
        wildcardQname = '*.local.lan'
        A = '192.168.0.2'

        remap = StaticRemap(qname=wildcardQname, A=A)
        self.assertIsNone(remap.has(qname='local.lan', type=QTYPE.A))

    def test_middleplace_wildcard_remap_success(self):
        wildcardQname = 'analysis.*.lan'
        TXT = 'page_type=analysis'

        remap = StaticRemap(qname=wildcardQname, TXT=TXT)
        self.assertEqual(remap.has('analysis.server.lan', QTYPE.TXT), TXT)

    def test_lastplace_wildcard_remap_success(self):
        wildcardQname = 'myserver.*'
        A = '192.168.0.2'

        remap = StaticRemap(qname=wildcardQname, A=A)

        self.assertEqual(remap.has('myserver.com', QTYPE.A), A)
        self.assertEqual(remap.has('myserver.net', QTYPE.A), A)

#########################
### STATIC VLAN TESTS ###
#########################

class StaticVlanTest(unittest.TestCase):
    def test_from_dict_success(self):
        vlan = StaticVlan(
            name='_vlan0',
            conf={
                '__vlanmask': '10.0.0.0/16',
                'qname': '10.0.0.1',
                'another-qname': {
                    'A' : '10.0.0.2',
                    'TXT' : ['txt record', 'another txt record'],
                    'CNAME': 'another-qname.lan'
                }
            }
        )

        self.assertEqual(vlan.search('qname', QTYPE.A), '10.0.0.1')
        self.assertEqual(vlan.search('another-qname', QTYPE.TXT), ['txt record', 'another txt record'])
        self.assertIsNone(vlan.search('another-qname', QTYPE.AAAA))

    def test_from_dict_fail_no_vlanmask(self):
        try:
            StaticVlan(
                name='_vlan0',
                conf={
                    'qname': '10.0.0.1',
                    'another-qname': {
                        'A': '10.0.0.2',
                        'TXT': ['txt record', 'another txt record'],
                        'CNAME': 'another-qname.lan'
                    }
                }
            )

        except SystemExit:
            pass

        else:
            self.fail('Test should have raised SystemExit')

    def test_from_dict_with_exclusions(self):
        vlan = StaticVlan(
            name='_vlan0',
            conf={
                '__vlanmask': '192.168.0.0/24',
                '__exclude': ['192.168.0.250', '192.168.0.251'],
                'qname': '192.168.0.2',
            }
        )

        self.assertTrue(vlan.allows('192.168.0.55'))
        self.assertFalse(vlan.allows('192.168.0.250'))
        self.assertFalse(vlan.allows('10.0.0.1'))

##################
### CONF TESTS ###
##################

class ConfTest(unittest.TestCase):
    def test_conf_from_yaml(self):
        yamlText = '''# configuration is explained in the README.md file at
# https://github.com/ryzeon-dev/bmdns

host: 0.0.0.0
port: 53

logging: yes
persistent-log: no

static:
  me.local: 0.0.0.0
  qname: 
    A: 192.168.1.1
    TXT: "txt record"

root-servers:
  - 1.1.1.1
  - 1.0.0.1
  - tls://1.1.1.1
  - tls://dns.cloudflare.com

blocklists:
  -'''

        fileName = tempfile.mktemp(prefix='bmdns_test', suffix='.yaml')

        with open(fileName, 'w') as file:
            file.write(yamlText)

        conf = Conf(fileName)


        self.assertEqual(conf.host, '0.0.0.0')
        self.assertEqual(conf.port, 53)
        self.assertEqual(conf.logging, True)
        self.assertEqual(conf.persistentLog, False)
        self.assertEqual(conf.rootServers, ['1.1.1.1', '1.0.0.1', 'tls://1.1.1.1', 'tls://dns.cloudflare.com'])
        self.assertEqual(conf.search('me.local', QTYPE.A), '0.0.0.0')
        self.assertEqual(conf.search('qname', QTYPE.TXT), 'txt record')
        self.assertIsNone(conf.search('name', QTYPE.CNAME))

########################
### VALIDATION TESTS ###
########################

class ValidationTests(unittest.TestCase):
    def test_ipv4_success(self):
        self.assertTrue(validateIPv4('10.2.0.0'))

    def test_ipv4_fail(self):
        self.assertFalse(validateIPv4('10.2.0.258'))

    def test_tls_ipv4_success(self):
        self.assertTrue(validateTlsIPv4('tls://1.1.1.1'))

    def test_tls_ipv4_fail(self):
        self.assertFalse(validateTlsIPv4('tsl://1.1.1.1'))

    def test_ipv6_success(self):
        self.assertTrue(validateIPv6('fe80:beef::deeb'))

    def test_ipv6_fail(self):
        self.assertFalse(validateIPv6('ffee:deeb::dggh'))

    def test_txt_success(self):
        self.assertTrue(validateTxtRecord('key=value'))

    def test_txt_fail(self):
        self.assertFalse(validateTxtRecord('a'*300))

    def test_cname_success(self):
        self.assertTrue(validateDomainName('domain.name.tld'))

    def test_cname_fail(self):
        self.assertFalse(validateDomainName('wrong_domain.name.a'))

    def test_tls_domain_name_success(self):
        self.assertTrue(validateTlsDomainName('tls://dns.cloudflare.com'))

    def test_tls_domain_name_fail(self):
        self.assertFalse(validateTlsDomainName('tsl://dns.cloudflare.com'))

    def test_vlanmask_success(self):
        self.assertTrue(validateVlanMask('192.168.0.1/24'))
        self.assertTrue(validateVlanMask('192.168.0.1'))

    def test_vlanmask_fail(self):
        self.assertFalse(validateVlanMask('192.168.256.1/24'))
        self.assertFalse(validateVlanMask('192.168.0.1/55'))

##################
### UTILS TEST ###
##################

class UtilsTests(unittest.TestCase):
    def test_encode_name(self):
        name = 'host.name.tld'
        encoded = encodeName(name)

        self.assertEqual(encoded, b'\x04host\x04name\x03tld\x00')

    def test_decode_name(self):
        encoded = b'\x04host\x04name\x03tld\x00'
        decoded = decodeName(encoded, 0)

        self.assertEqual(decoded, 'host.name.tld')

        encoded = b'\x01\x02\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04host\x04name\x03tld\x00\x00\x00\x00\x01\xc0\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
        decoded = decodeName(encoded, 31)
        self.assertEqual(decoded, 'host.name.tld')

    def test_check_bit_flag(self):
        self.assertTrue(checkBitFlag(0b10100101, 0b00100000))
        self.assertFalse(checkBitFlag(0, 0b01000000))

    def test_ipv4_to_bytes(self):
        self.assertEqual(ipToBytes('127.0.0.1'), b'\x7F\x00\x00\x01')
        self.assertEqual(ipToBytes('192.168.64.1'), b'\xC0\xA8\x40\x01')

    def test_ipv6_to_bytes(self):
        self.assertEqual(ipv6ToBytes('ffee:beef::deeb'), b'\xff\xee\xbe\xef\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xde\xeb')
        self.assertEqual(ipv6ToBytes('fe80:deb:beef::beef:deb'), b'\xfe\x80\r\xeb\xbe\xef\x00\x00\x00\x00\x00\x00\xbe\xef\r\xeb')

if __name__ == '__main__':
    unittest.main()