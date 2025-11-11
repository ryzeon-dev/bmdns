if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
  exit 1
fi

if [ "$(ls | grep src)" == "" ]; then
  echo "Do not run update script inside of `scripts` directory. Run it from the `bmdns` directory"
  exit 1
fi

if [ "$(systemctl status bmdns | grep "Active: active")" ]; then
  systemctl stop bmdns
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
mkdir -p /var/log/bmdns

if [ -f /etc/bmdns/bmdns.service ]; then
  rm /etc/bmdns/bmdns.service
fi

cp ./conf/bmdns.service /etc/systemd/system/bmdns.service

systemctl daemon-reload
systemctl restart bmdns