if [ "$(id -u)" != "0" ]; then
  echo "Execution requires root"
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
systemctl daemon-reload
systemctl restart bmdns