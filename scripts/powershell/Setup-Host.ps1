# Установка зависимостей backend (venv + pip) и frontend (npm) на хосте Windows.
#   .\scripts\powershell\Setup-Host.ps1
#   .\scripts\powershell\Setup-Host.ps1 -System   # LibreOffice / Tesseract (winget/choco)

param(
    [switch]$System,
    [switch]$Help
)

. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @"
Использование: Setup-Host.ps1 [-System] [-Help]

  -System  Установить LibreOffice и Tesseract через winget или Chocolatey
  -Help    Эта справка

Создаёт backend\.venv, frontend\node_modules, .env и backend\storage.
"@ | Write-Host
    exit 0
}

$RepoRoot = Get-PteRepoRoot
Write-PteHostBanner -Title "PTE-DocEx — установка на хосте (Windows)"
Assert-PteHostPrereqs -RequireNode

$backendDir = Join-Path $RepoRoot "backend"
$frontendDir = Join-Path $RepoRoot "frontend"
$venvDir = Join-Path $backendDir ".venv"

$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command py -ErrorAction Stop
    $pythonExe = "py -3"
} else {
    $pythonExe = $pythonCmd.Source
}

Write-Host "Репозиторий: $RepoRoot"
Write-Host "Python: $pythonExe"

if (-not (Test-Path -LiteralPath $venvDir)) {
    Write-Host "Создание venv в backend\.venv ..."
    if ($pythonExe -eq "py -3") {
        & py -3 -m venv $venvDir
    } else {
        & $pythonExe -m venv $venvDir
    }
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt")

$storageDir = Join-Path $backendDir "storage"
if (-not (Test-Path -LiteralPath $storageDir)) {
    New-Item -ItemType Directory -Path $storageDir | Out-Null
}

Ensure-PteDotenv -RepoRoot $RepoRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

Write-Host "npm install (frontend) ..."
Push-Location $frontendDir
try {
    if (Test-Path -LiteralPath "package-lock.json") {
        npm ci
    } else {
        npm install
    }
} finally {
    Pop-Location
}

if ($System) {
    & (Join-Path $PSScriptRoot "Install-SystemDeps.ps1")
}

Write-Host ""
Write-Host "Готово. Дальше:" -ForegroundColor Green
Write-Host "  1) ollama serve"
Write-Host "  2) ollama pull $(if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { 'llama3.1:8b' })"
Write-Host "  3) .\scripts\powershell\Start-Host.ps1"
Write-Host ""
Write-Host "Проверка: .\scripts\powershell\Check-Host.ps1" -ForegroundColor DarkGray
Write-Host "Остановка: .\scripts\powershell\Stop-Host.ps1" -ForegroundColor DarkGray
if (-not $System) {
    Write-Host ""
    Write-Host "OCR и сравнение DOCX: .\scripts\powershell\Install-SystemDeps.ps1" -ForegroundColor DarkYellow
}
