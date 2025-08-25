#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
fi

python3 -m venv venv

source venv/bin/activate
pip install pyinstaller pyyaml

pyinstaller --onefile ./src/main.py --name bare-metal-dns
mkdir -p bin
mv ./dist/bare-metal-dns ./bin

deactivate
rm -rf build dist bare-metal-dns.spec venv

cp ./bin/bare-metal-dns /usr/local/bin
mkdir -p /etc/bmdns

mkdir -p /usr/local/share/bmdns
touch /usr/local/share/bmdns/bmdns.log

cp ./sample_conf.yaml /etc/bmdns/conf.yaml
cp ./bmdns.service /etc/bmdns/bmdns.service

systemctl enable /etc/bmdns/bmdns.service
systemctl start bmdns.service