if not exists "src" (
    echo "Do not run update script inside of `scripts` directory. Run it from the `bmdns` directory"
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

copy .\bin\bare-metal-dns.exe "%PROGRAMFILES(X86)%\bmdns\bin\bare-metal-dns.exe" /Y