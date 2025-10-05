python -m venv venv

set oldPath="%PATH%"
set PATH=".\venv\Scripts;%PATH%"

.\venv\Scripts\python.exe -m pip install pyinstaller pyyaml
.\venv\Scripts\pyinstaller --onefile .\src\main.py --hidden-import="yaml" --name bare-metal-dns

set PATH="%oldPath%"
mkdir .\bin

copy .\dist\bare-metal-dns.exe .\bin\bare-metal-dns.exe /Y
rmdir .\dist .\build .\venv /s /q

mkdir "%PROGRAMFILES(X86)%\bmdns"
mkdir "%PROGRAMFILES(X86)%\bmdns\bin"
mkdir "%PROGRAMFILES(X86)%\bmdns\log"

copy .\bin\bare-metal-dns.exe "%PROGRAMFILES(X86)%\bmdns\bin\bare-metal-dns.exe" /Y
copy .\sample_conf.yaml "%PROGRAMFILES(X86)%\bmdns\conf.yaml" /Y