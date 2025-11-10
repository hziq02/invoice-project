# PowerShell script to run Django server with venv
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Activate virtual environment
& "$scriptPath\venv\Scripts\Activate.ps1"

# Run the server
python manage.py runserver

