@echo off
setlocal
cd /d "%~dp0"
title An Cu - Quan ly thue can ho
if not exist ".venv\Scripts\python.exe" (
    echo Chua co moi truong Python. Hay cai dat theo README.md.
    pause
    exit /b 1
)
if not exist "data\db.sqlite3" (
    echo Chua co co so du lieu. Hay chay tools\setup_local.ps1 truoc.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -c "import socket,sys; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('127.0.0.1',8000)); s.close(); sys.exit(0 if result==0 else 1)"
if not errorlevel 1 (
    start "" "http://127.0.0.1:8000"
    exit /b 0
)
echo Dang khoi dong An Cu...
echo Dia chi: http://127.0.0.1:8000
echo Giu cua so nay mo trong khi su dung. Nhan Ctrl+C de dung.
start "" /b powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:8000'"
".venv\Scripts\python.exe" -u -X utf8 manage.py runserver 127.0.0.1:8000 --noreload
pause
