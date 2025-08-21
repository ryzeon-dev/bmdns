#!/bin/bash

systemctl stop bmdns
systemctl disable bmdns

rm -rf /etc/bmdns
rm -rf /usr/local/share/bmdns/
rm /usr/local/bin/bare-metal-dns