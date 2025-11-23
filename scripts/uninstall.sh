#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
fi

echo 'Stopping and disabling systemd service'
systemctl stop bmdns
systemctl disable bmdns

echo 'Removing configuration and log directories'
rm -rf /etc/bmdns
rm -rf /var/log/bmdns

echo 'Removing binaries'
rm /usr/local/bin/bare-metal-dns
