@echo off
cd /d %~dp0
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Activating venv failed. Trying direct Python path...
    venv\Scripts\python.exe manage.py runserver
) else (
    python manage.py runserver
)
pause

