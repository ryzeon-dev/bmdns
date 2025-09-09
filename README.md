# Bare-Metal DNS
Simple IPv4-only DNS written in Python. No fancy UI. No extensive analysis. Just a bare metal DNS server

## Warning
The software has only been tested on GNU/Linux, at the moment. Its behaviour is unknown on other Operative Systems 
(it is expected to work just fine on BSD distributions).

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

persistent-log: false

static:
  me.local: 0.0.0.0

root-servers:
  - 1.1.1.1
  - 1.0.0.1

blocklists:
  -
```

### Static remaps
To add a personalized dns resolution, add the hostname with its ip address to `static` section. 

e.g. you have a server named `my-server` with ip address `192.168.0.2`
```yaml
static:
  my-server: 192.168.0.2
```
<br/> 
<br/>


BMDNS's static remaps support vlans. This way a single DNS server can be used for multiple vlans (provided that the host has the ability to access all of them).
When using vlans, only the requestant whose address belongs to a certain vlan may access its static remaps.

e.g. you have two vlans (with addresses `192.168.0.0` and `192.168.1.0`), and you have a server that lives on both named `my-server` with ip addresses (respectively) `192.168.0.2` and `192.168.1.2` 
```yaml 
static:
  me.local: 0.0.0.0
  
  _vlan0: 
    __vlanmask: 192.168.0.0/24
    my-server: 192.168.0.2

  _vlan1:
    __vlanmask: 192.168.1.0/24
    my-server: 192.168.1.2
```
When creating a vlan space, a certain syntax is required:
- a vlan name must start with `_vlan`, which tells the configuration parser to create a new vlan static space
- inside the just created vlan object, create an object named `__vlanmask` with `<ip-address>/<cidr>` as value
  - if no `cidr` is specified, `24` is assumed
- then follow with the static remaps


### Root Servers
At least one root server is required for BMDNS to work properly. \
Root servers are queried when BMDNS doesn't have the answer in its cache or in the static mapping

e.g. you want to use AdGuard as DNS root server
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
  - internal cache is used for both IPv4 and CNAME queries 
- static mappings
- blocklist files
- root server

Useful note: static mappings are faster to search into than blocklist files 

## Log
If log-persistency is set to `false`, BMDNS writes its log in the file `/usr/local/share/bmdns/bmdns.log`, which is created during the installation process. 
The log is wiped at every restart of the service  

If log-persistency is set to `true`, BMDNS will create a new file at every restart of the service, naming it `bmdns_[$date]_[$time].log`.