@echo off
setlocal
cd /d "%~dp0" || exit /b 1

if not exist "venv\Scripts\python.exe" (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Gagal membuat virtual environment. Pastikan Python sudah terpasang.
        pause
        exit /b 1
    )
)

"venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Instalasi dependency gagal. Periksa koneksi internet dan requirements.txt.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo [ERROR] Aplikasi berhenti dengan error.
    pause
    exit /b 1
)

endlocal