#!/bin/bash

if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
fi

if [ ! -d "src" ]; then
  echo 'Do not run installation script inside of `scripts` directory. Run it from the `bmdns` directory'
  exit 1
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

echo 'Creating `/etc/bmdns` and `/var/log/bmdns` directories'
mkdir -p /etc/bmdns
mkdir -p /var/log/bmdns

echo 'Creating configuration and log files'
touch /var/log/bmdns/bmdns.log
cp ./conf/sample_conf.yaml /etc/bmdns/conf.yaml

echo 'Installing, enabling and starting systemd service'
cp ./conf/bmdns.service /etc/bmdns/bmdns.service
systemctl enable /etc/bmdns/bmdns.service
systemctl start bmdns.service