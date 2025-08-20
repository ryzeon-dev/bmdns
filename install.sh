#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
endif

python3 -m venv venv

source venv/bin/activate
pip install pyinstaller pyyaml

pyinstaller --onefile main.py --name bare-metal-dns
mkdir bin
mv ./dist/bare-metal-dns ./bin

rm -rf build dist bare-metal-dns.spec
deactivate

cp ./bin/bare-metal-dns /usr/local/bin
mkdir /etc/bmdns

cp ./sample_conf.yaml /etc/bmdns/conf.yaml
systemctl enable $(pwd)/bmdns.service

systemctl start bmdns.service