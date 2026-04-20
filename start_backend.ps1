# start_backend.ps1
Write-Host "Checking if venv exists..."
$VenvPath = ".\backend\venv\Scripts\Activate.ps1"
if (-Not (Test-Path $VenvPath)) {
    Write-Host "Virtual environment not found at $VenvPath" -ForegroundColor Red
    exit 1
}

Write-Host "Starting Data Update Microservice..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\Projects\Documind; .\backend\venv\Scripts\Activate.ps1; python backend\run_data_microservice.py"

Write-Host "Starting Celery Beat (Scheduler)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\Projects\Documind; .\backend\venv\Scripts\Activate.ps1; celery -A backend.celery_app beat --loglevel=info"

Write-Host "Starting FastAPI Main Server (and Celery Worker)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd d:\Projects\Documind; .\backend\venv\Scripts\Activate.ps1; python backend\main.py"

Write-Host "All backend processes launched in separate windows!" -ForegroundColor Cyan
