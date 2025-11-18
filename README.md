<p align="center">
<img alt="Version Badge" src="https://img.shields.io/badge/dev--version-v4.1.0-16a085">
<img alt="Version Badge" src="https://img.shields.io/badge/release-v4.0.0-16a085">
<img alt="Docker Image Version" src="https://img.shields.io/docker/v/ryzeondev/bmdns?label=docker-version&color=16a085">
<img alt="License Badge" src="https://img.shields.io/github/license/ryzeon-dev/bmdns?color=16a085">
<img alt="Language Badge" src="https://img.shields.io/badge/python3-16a085?logo=python&logoColor=16a085&labelColor=5a5a5a">
</p>

# Bare-Metal DNS
Lightweight DNS written in Python. No fancy UI. No extensive analysis. Just a bare metal DNS server

# Index
- [Supported OS](#supported-os) 
- [OS Requirements](#os-requirements) 
- [Log Analyzer - BMDLA](#log-analyzer---bmdla)
- [Install](#install)   
  - [Linux](#linux) 
  - [Debian](#debian)
  - [Windows](#windows)
  - [Docker](#docker)
- [Update](#update)
  - [Linux](#linux-1)
  - [Windows](#windows-1)
- [Uninstall](#uninstall)
  - [Linux](#linux-2)
  - [Windows](#windows-2)
- [Configuration](#configuration)
  - [Static Remaps](#static-remaps)
  - [VLANs](#vlans)
  - [Root Servers](#root-servers)
  - [Blocklists](#blocklists)
- [Cascading Search](#cascading-search)
- [Log](#log)


## Supported OS
The software officially supports GNU/Linux and Windows. 

It should work on FreeBSD and MacOS systems, but it is untested.  
The `install`/`update`/`uninstall` scripts are specifically written for GNU/Linux and Windows, any attempt of running them in other OS may lead to errors and unexpected behaviour. 

## OS requirements
Compilation requires `python3 python3-venv python3-pip` packages to be installed. Install them using your OS's package manager

e.g.
```commandline
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

## Log Analyzer - BMDLA
[BMDLA](https://github.com/ryzeon-dev/bmdla) is the software specifically written to analyze the log files from BMDNS. \
It provides a series of actions, allowing to check for most requested domains, most active requestants and more.

## Install
### Linux
On Linux run the installation script as root
```commandline
sudo bash ./scripts/install.sh
```
The installation script 
- compiles the software
- creates the required directories (`/etc/bmdns` and `/var/log/bmdns`)
- copies the default configuration file into `/etc/bmdns/conf.yaml`
- installs the compiled binary (into `/usr/local/bin`) 
- adds `bmdns.service` to systemd services 

### Debian
Run the following line in a dedicated directory
```commandline
wget https://github.com/ryzeon-dev/bmdns/releases/download/v4.0.0/bmdns_4.0.0_amd64.deb && sudo dpkg -i ./bmdns_*_amd64.deb && sudo systemctl enable bmdns && sudo systemctl start bmdns
```

Warning: the executables were compiled and packed into .deb on Debian 13, the package might not work on older Debian releases (because of glibc versions)  

### Windows
On Windows run the installation script as an administrator:
```commandline
.\scripts\install.bat
```
The installation script 
- compiles the software 
- creates the required directories (`%PROGRAMFILES%\bmdns\`, `%PROGRAMFILES%\bmdns\bin\`, `%PROGRAMFILES%\bmdns\log\`) 
- copies the default configuration file into `%PROGRAMFILES%\bmdns\conf.yaml`
- installs the compiled binary into  `%PROGRAMFILES%\bmdns\bin\`

In order to create a Service for this software, you'll need to use some intermediary, such as [srvany](https://github.com/birkett/srvany-ng) or [alwaysup](https://github.com/always-up-app/always-up-app)

### Docker
[DockerHub Repository](https://hub.docker.com/r/ryzeondev/bmdns)

To instance `bmdns` in a docker container, run the following command 
```commandline
sudo docker run --name <name> -p 53:53/udp --mount type=bind,src=<conf-mountpoint>,dst=/etc/bmdns ryzeondev/bmdns:latest
```
Replace:
- `<name>` with the name you want to give the container 
- `<conf-mountpoint>` with  a local directory where to mount `/etc/bmdns` from the container; this allows to edit the configuration file


Optionally, you can add `--mount type=bind,src=<log-mountpoint>,dst=/var/log/bmdns` argument, replacing `<log-mountpoint>` 
with a local directory where to mount `/var/log/bmdns` from the container; this allows to inspect log file(s)

## Update
The `update` script compiles and installs a new version of `bmdns` without touching the existing configuration files

### Linux
On Linux run the update script as root
```commandline
sudo bash ./scripts/update.sh
```

### Windows
On windows run the update script as an administrator
```commandline
.\scripts\update.bat
```

## Uninstall
### Linux
On Linux run the uninstallation script as root
```commandline
sudo bash ./scripts/uninstall.sh
```

### Windows
On Windows run the uninstallation script as an administrator
```commandline
.\scripts\uninstall.bat
```

## Configuration
Configuration involves editing:
- `/etc/bmdns/conf.yaml` file on linux systems
- `%PROGRAMFILES%/bmdns/conf.yaml` on windows systems

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

Static remap supports A, AAAA, TXT and CNAME types.

e.g. you have a server named `my-server` with ip address `192.168.0.2` \
To only set IPv4 (A) resolution, just specify as follows
```yaml
static:
  my-server: 192.168.0.2
```

To set multiple resolution types for the same domain name, specify as follows 
```yaml
static:
    my-server:
      A: 192.168.0.2
      TXT: key=value
      AAAA: fe80:deeb::beef
      CNAME: my-server.lan
```
Note that record types can be omitted if not needed (e.g. you only want to set IPv4 [A] and IPv6 [AAAA] types)

```yaml
static:
    my-server:
      A: 192.168.0.2
      AAAA: fe80:deeb::beef
```

TXT records can be multiple. To set more than one record, write them in a yaml list after the TXT identifier
```yaml
static:
  my-server:
    A: 192.168.0.2
    TXT:
      - key=value
      - my_verification_string
      - very_important_dns_txt_record
```

<br/>

### VLANs
BMDNS's static remaps support vlans. This way a single DNS server can be used for multiple vlans (provided that the host has the ability to access all of them).
When using vlans, only the requestant whose address belongs to a certain vlan may access its static remaps.

Vlan remaps follow the same syntax-scheme as standard remaps

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

#### VLAN lock
BMDNS vlans can be configured to block access to external resolutions (root server's ones), 
and only allow satic vlan remaps to be forwarded.\
To do so, add `__block-external: yes` to your vlan configuration

```yaml
static:
  _vlan0:
    __vlankmask: 192.168.0.0/24
    __block-external: yes
```


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
- static mappings
- blocklist files
- internal cache 
- root servers

Useful note: static mappings are faster to search into than blocklist files 

## Log
Log files are written into:
- `/var/log/bmdns/` directory on linux systems
- `%PROGRAMFILES%/bmdns/log/` directory on windows systems

If log-persistency is set to `false`, BMDNS writes its log in the file `LOG_DIR/bmdns.log`, which is created during the installation process. 
The log is wiped at every restart of the service  

If log-persistency is set to `true`, BMDNS will create a new file at every restart of the service, naming it `bmdns_[$date]_[$time].log`.