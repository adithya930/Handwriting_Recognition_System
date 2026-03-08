# Automated Setup Script for Handwriting Recognition System
# Run this script in PowerShell to automate the setup process

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Handwriting Recognition System - Automated Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Python
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
    
    # Check if version is 3.8+
    $version = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>&1
    if ([float]$version -lt 3.8) {
        Write-Host "✗ Python 3.8+ required. Current version: $version" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Step 2: Check MySQL
Write-Host ""
Write-Host "[2/8] Checking MySQL installation..." -ForegroundColor Yellow
$mysqlService = Get-Service -Name "MySQL*" -ErrorAction SilentlyContinue
if ($mysqlService) {
    Write-Host "✓ MySQL service found: $($mysqlService.Name)" -ForegroundColor Green
    if ($mysqlService.Status -ne "Running") {
        Write-Host "! MySQL is not running. Starting service..." -ForegroundColor Yellow
        Start-Service $mysqlService.Name
        Write-Host "✓ MySQL started" -ForegroundColor Green
    }
} else {
    Write-Host "⚠ MySQL service not found. Please ensure MySQL is installed." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Step 3: Create Virtual Environment
Write-Host ""
Write-Host "[3/8] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "! Virtual environment already exists" -ForegroundColor Yellow
    $recreate = Read-Host "Recreate? (y/n)"
    if ($recreate -eq "y") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✓ Virtual environment recreated" -ForegroundColor Green
    }
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Step 4: Activate Virtual Environment
Write-Host ""
Write-Host "[4/8] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Step 5: Upgrade pip
Write-Host ""
Write-Host "[5/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✓ pip upgraded" -ForegroundColor Green

# Step 6: Install Dependencies
Write-Host ""
Write-Host "[6/8] Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take 5-10 minutes..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Failed to install some dependencies" -ForegroundColor Red
    Write-Host "   Try running: pip install -r requirements.txt" -ForegroundColor Yellow
}

# Step 7: Setup Environment File
Write-Host ""
Write-Host "[7/8] Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "! Please edit .env file with your MySQL credentials" -ForegroundColor Yellow
} else {
    Write-Host "! .env file already exists" -ForegroundColor Yellow
}

# Step 8: Database Setup
Write-Host ""
Write-Host "[8/8] Database setup..." -ForegroundColor Yellow
Write-Host "   Please run the database schema manually:" -ForegroundColor Cyan
Write-Host "   mysql -u root -p handwriting_db < database_schema.sql" -ForegroundColor White
Write-Host ""

# Summary
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Edit .env file with your MySQL credentials" -ForegroundColor White
Write-Host "2. Create database: CREATE DATABASE handwriting_db;" -ForegroundColor White
Write-Host "3. Run schema: mysql -u root -p handwriting_db < database_schema.sql" -ForegroundColor White
Write-Host "4. Train model: python backend\models\train_model.py --synthetic" -ForegroundColor White
Write-Host "5. Start server: python backend\app.py" -ForegroundColor White
Write-Host "6. Open browser: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "For detailed instructions, see QUICKSTART.md" -ForegroundColor Cyan
Write-Host ""

# Offer to open documentation
$openDocs = Read-Host "Open QUICKSTART.md? (y/n)"
if ($openDocs -eq "y") {
    Start-Process "QUICKSTART.md"
}

Write-Host "Setup script completed!" -ForegroundColor Green
