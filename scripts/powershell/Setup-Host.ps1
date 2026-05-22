# Install backend (venv + pip) and frontend (npm) on Windows host.
#   .\scripts\powershell\Setup-Host.ps1
#   .\scripts\powershell\Setup-Host.ps1 -System

param(
    [switch]$System,
    [switch]$Help
)

. (Join-Path $PSScriptRoot "_common.ps1")

if ($Help) {
    @"
Usage: Setup-Host.ps1 [-System] [-Help]

  -System  Install LibreOffice and Tesseract via winget or Chocolatey
  -Help    Show this help

Creates backend/.venv, frontend/node_modules, .env, and backend/storage.
"@ | Write-Host
    exit 0
}

$RepoRoot = Get-PteRepoRoot
Write-PteHostBanner -Title "PTE-DocEx — host setup (Windows)"
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

Write-Host "Repository: $RepoRoot"
Write-Host "Python: $pythonExe"

if (-not (Test-Path -LiteralPath $venvDir)) {
    Write-Host "Creating venv in backend/.venv ..."
    if ($pythonExe -eq "py -3") {
        & py -3 -m venv $venvDir
    } else {
        & $pythonExe -m venv $venvDir
    }
}

$venvPython = Join-PtePath $venvDir @("Scripts", "python.exe")
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

$defaultModel = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "llama3.1:8b" }

Write-Host ""
Write-Host "Done. Next steps:" -ForegroundColor Green
Write-Host "  1) ollama serve"
Write-Host "  2) ollama pull $defaultModel"
Write-Host "  3) .\scripts\powershell\Start-Host.ps1"
Write-Host ""
Write-Host "Check:  .\scripts\powershell\Check-Host.ps1" -ForegroundColor DarkGray
Write-Host "Stop:   .\scripts\powershell\Stop-Host.ps1" -ForegroundColor DarkGray
if (-not $System) {
    Write-Host ""
    Write-Host "OCR / DOCX compare: .\scripts\powershell\Install-SystemDeps.ps1" -ForegroundColor DarkYellow
}
