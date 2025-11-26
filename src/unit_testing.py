import unittest
import tempfile

from StaticRemap import StaticRemap
from qtype import QTYPE
from StaticVlan import StaticVlan
from Conf import Conf
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
        self.assertEqual(conf.rootServers, ['1.1.1.1', '1.0.0.1'])
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

if __name__ == '__main__':
    unittest.main()