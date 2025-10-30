if not exists "src" (
    echo "Do not run installation script inside of `scripts` directory. Run it from the `bmdns` directory"
    exit /b 1
)

python -m venv venv

set oldPath="%PATH%"
set PATH=".\venv\Scripts;%PATH%"

.\venv\Scripts\python.exe -m pip install pyinstaller pyyaml
.\venv\Scripts\pyinstaller --onefile .\src\main.py --hidden-import="yaml" --name bare-metal-dns

set PATH="%oldPath%"
mkdir .\bin

copy .\dist\bare-metal-dns.exe .\bin\bare-metal-dns.exe /Y
rmdir .\dist .\build .\venv /s /q

mkdir "%PROGRAMFILES%\bmdns"
mkdir "%PROGRAMFILES%\bmdns\bin"
mkdir "%PROGRAMFILES%\bmdns\log"

copy .\bin\bare-metal-dns.exe "%PROGRAMFILES%\bmdns\bin\bare-metal-dns.exe" /Y
copy .\sample_conf.yaml "%PROGRAMFILES%\bmdns\conf.yaml" /Y