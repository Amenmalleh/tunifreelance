# TuniFreelance Project Runner
# This script automates the setup and execution of the database, backend, and frontend.

$ErrorActionPreference = "Stop"

Write-Host "`n🚀 Starting TuniFreelance Project Setup..." -ForegroundColor Cyan

# 1. Handle Virtual Environment
if (Test-Path ".venv") {
    Write-Host "Activating Virtual Environment..." -ForegroundColor Gray
    . .venv\Scripts\Activate.ps1
}

# 2. Setup Backend & Database
Write-Host "`n[1/3] Setting up Database & Backend..." -ForegroundColor Yellow
Set-Location "backend"

# Ensure dependencies are installed
Write-Host "Checking/Installing backend dependencies..." -ForegroundColor Gray
pip install -r requirements.txt

# Create Database if not exists
Write-Host "Creating database (MySQL)..." -ForegroundColor Gray
try {
    python create_db.py
} catch {
    Write-Host "`n❌ MySQL Error: Access Denied." -ForegroundColor Red
    Write-Host "Please check your MySQL password in 'backend/.env' and try again." -ForegroundColor Yellow
    Write-Host "Current settings: " -ForegroundColor Gray
    if (Test-Path ".env") { Get-Content ".env" | Select-String "DB_USER|DB_PASSWORD" }
    Set-Location ".."
    exit
}

# Apply Migrations
Write-Host "Applying migrations..." -ForegroundColor Gray
try {
    python manage.py migrate
} catch {
    Write-Host "`n❌ Django Migration Error." -ForegroundColor Red
    Write-Host "TIP: If you see a MariaDB version error, I've downgraded Django in requirements.txt to fix it." -ForegroundColor Gray
    Write-Host "Please ensure your MySQL server is running and credentials in 'backend/.env' are correct." -ForegroundColor Yellow
    Set-Location ".."
    exit
}

# Start Backend Server in a new window
Write-Host "Starting Django Backend Server on http://localhost:8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "if (Test-Path '../.venv') { . ../.venv/Scripts/Activate.ps1 }; python manage.py runserver 8001" -WindowStyle Normal

Set-Location ".."

# 3. Setup Frontend
Write-Host "`n[2/3] Setting up Frontend (Angular)..." -ForegroundColor Yellow

# Start Frontend Server in a new window
Write-Host "Starting Angular Frontend Server on http://localhost:4200..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npm start" -WindowStyle Normal

# 4. Final Step
Write-Host "`n[3/3] Success! Both servers are starting up." -ForegroundColor Cyan
Write-Host "-------------------------------------------------------"
Write-Host "Backend: http://localhost:8001" -ForegroundColor Blue
Write-Host "Frontend: http://localhost:4200" -ForegroundColor Blue
Write-Host "-------------------------------------------------------"
Write-Host "Please wait a few seconds for the servers to be ready."
Write-Host "Press any key to exit this setup script..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
