@echo off
rem Gera o executavel do jogo: dist\ArenaDeCombate.exe
rem Precisa do ambiente .venv com as bibliotecas:  .venv\Scripts\python.exe -m pip install -r requirements.txt
cd /d "%~dp0"
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name ArenaDeCombate ^
    --add-data "interface;interface" ^
    app.py
echo.
echo Pronto: dist\ArenaDeCombate.exe
