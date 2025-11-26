#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
fi

if [ "$(ls | grep src)" == "" ]; then
  echo "Do not run update script inside of `scripts` directory. Run it from the `bmdns` directory"
  exit 1
fi

if [ "$(systemctl status bmdns | grep "Active: active")" ]; then
  echo 'Stopping systemd service'
  systemctl stop bmdns
fi

echo 'Creating virtual environment for python compilation'
python3 -m venv venv > /dev/null

if [ "$?" != "0" ]; then
  echo 'Error while creating python virtual environment. Aborting installation'
  exit 1
fi

source venv/bin/activate

echo 'Installing dependencies'
pip install pyinstaller pyyaml > /dev/null

if [ "$?" != "0" ]; then
  echo 'Error while installing dependencies. Aborting installation'
  exit 1
fi

echo 'Compiling python binary'
pyinstaller --onefile ./src/main.py --name bare-metal-dns &> /dev/null

if [ "$?" != "0" ]; then
  echo 'Error while compiling. Aborting installation'
  exit 1
fi

mkdir -p bin
mv ./dist/bare-metal-dns ./bin

echo 'Cleaning up compilation environment'
deactivate
rm -rf build dist bare-metal-dns.spec venv

echo 'Installing binary'
cp ./bin/bare-metal-dns /usr/local/bin

mkdir -p /var/log/bmdns

echo
if [ -f /etc/bmdns/bmdns.service ]; then
  rm /etc/bmdns/bmdns.service
fi

echo 'Installing, enabling and starting systemd service'
cp ./conf/bmdns.service /etc/bmdns/bmdns.service
systemctl daemon-reload
systemctl restart bmdns