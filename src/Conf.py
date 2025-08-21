import yaml
import re

class Conf:
    def __init__(self, confPath: str):
        self.confPath = confPath
        self.remaps = {}

        self.__parseConf()
        self.__parseAdlists()

    def __parseConf(self):
        with open(self.confPath, 'r') as file:
            yconf = yaml.load(file, Loader=yaml.FullLoader)

        self.host = yconf['host']
        self.port = yconf['port']
        self.static = yconf['static']
        self.rootServers = yconf['root-servers']
        self.blocklists = yconf['blocklists']

    def __parseAdlists(self):
        for filePath in self.blocklists:
            if not filePath:
                continue

            self.__parseAdlist(filePath)

    def __parseAdlist(self, filePath: str):
        with open(filePath, 'r') as file:
            content = file.read()

        for line in content.split('\n'):
            if line.strip().startswith('#') or not line:
                continue

            chunks = line.strip().split(' ')
            ip = chunks[0].strip()

            hostname = chunks[1].strip()
            hostnameRegex = r'{}'.format(hostname.replace('.', r'\.').replace('*', '.*'))

            self.remaps[hostnameRegex] = ip

    def search(self, target: str) -> str|None:
        ip = self.static.get(target)
        if ip is not None:
            return ip

        for pattern, ip in self.remaps.items():
            if re.match(pattern, target):
                return ip

if __name__ == '__main__':
    conf = Conf('./conf.yaml', ['adlist.txt'])

    print(conf.remaps)
    print(conf.search('www.google.com'))