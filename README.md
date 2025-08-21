# Bare-Metal DNS
Simple DNS written in Python. No fancy UI. No extensive analysis. Just a bare metal DNS server

## Warning
The software has only been tested on GNU/Linux, at the moment. Its behaviour is unknown on other Operative Systems (it is expected to work just fine on BSD distributions).

## OS requirements
Compilation requires `python3 python3-venv python3-pip` packages to be installed 

## Install
Run the installation script as root
```commandline
sudo bash install.sh
```

## Uninstall
Run the uninstallation script as root
```commandline
sudo bash uninstall.sh
```

## Configuration
Configuration involves editing `/etc/bmdns/conf.yaml` file.

A sample configuration file is
```yaml
host: 0.0.0.0
port: 53

static:
  me.local: 0.0.0.0

root-servers:
  - 1.1.1.1
  - 1.0.0.1

blocklists:
  -
```

### Static remaps
To add a personalized dns resolution, add the hostname with its ip address to `static` section

e.g. you have a server named `my-server` with ip address `192.168.0.2`
```yaml
static:
  my-server: 192.168.0.2
```

### Root Servers
At least one root server is required for BMDNS to work properly. \
Root servers are queried when BMDNS doesn't have the answer in its cache or in the static mapping

e.g. you want to use AdGuard as DNS root servers
```yaml
root-servers:
  - 94.140.14.14
  - 94.140.15.15    
```

### Blocklists
List of text files which contain static mappings for websites you want to block

e.g. you have a blocklist file at `/opt/adlist.txt` which contains
```
0.0.0.0 ads.google.com
0.0.0.0 *advertising*
0.0.0.0 *ads*
```

Its file path has to be added under `blocklists` section
```yaml
blocklists:
  - /opt/adlist.txt
```

## Cascading search
BMDNS searches for an answer to a given query in the following order:
- internal cache
- static mappings
- blocklist files
- root server

 Useful note: static mappings are faster to search into than blocklist files 