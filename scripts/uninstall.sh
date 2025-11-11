#!/bin/bash

systemctl stop bmdns
systemctl disable bmdns

rm -rf /etc/bmdns
rm -rf /var/log/bmdns
rm /usr/local/bin/bare-metal-dns
rm /etc/systemd/system/bmdns.service