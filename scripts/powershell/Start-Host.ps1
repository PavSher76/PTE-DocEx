# Start LanguageTool, backend, and frontend on Windows host.
#
# Separate PowerShell windows (default):
#   .\scripts\powershell\Start-Host.ps1
#
# Background mode (logs in .pte-host/):
#   .\scripts\powershell\Start-Host.ps1 -Background
#
# Frontend in current window:
#   .\scripts\powershell\Start-Host.ps1 -Foreground

param(
    [switch]$SkipLanguageTool,
    [switch]$SkipSetupCheck,
    [switch]$Background,
    [switch]$Foreground,
    [switch]$Help
)

. (Join-Path $PSScriptRoot "_common.ps1")

if ($Help) {
    @"
Usage: Start-Host.ps1 [options]

  (default)          LanguageTool, backend, frontend in separate PowerShell windows
  -Background        All services in background; logs: .pte-host/backend.log, frontend.log
  -Foreground        LT + backend in background; frontend in current window
  -SkipLanguageTool  Do not start LanguageTool
  -SkipSetupCheck    Do not run Setup-Host when venv/node_modules are missing
  -Help              Show this help

Requires Ollama on host: ollama serve && ollama pull llama3.1:8b
"@ | Write-Host
    exit 0
}

if ($Background -and $Foreground) {
    throw "Use only one mode: -Background or -Foreground."
}

$RepoRoot = Get-PteRepoRoot
$ps1Dir = $PSScriptRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

Write-PteHostBanner -Title "PTE-DocEx — host start (Windows)"

if (-not $SkipSetupCheck) {
    $venvPython = Get-PteVenvPythonPath -RepoRoot $RepoRoot
    $nodeModules = Join-PtePath $RepoRoot @("frontend", "node_modules")
    if (-not ((Test-Path -LiteralPath $venvPython) -and (Test-Path -LiteralPath $nodeModules))) {
        Write-Host "Missing backend/.venv or frontend/node_modules. Running Setup-Host.ps1 ..." -ForegroundColor Yellow
        & (Join-Path $ps1Dir "Setup-Host.ps1")
    }
}

function Start-PteLanguageTool {
    if ($SkipLanguageTool) {
        Write-Host "LanguageTool skipped (-SkipLanguageTool)." -ForegroundColor DarkYellow
        return
    }
    if (-not (Test-PteCommand "docker")) {
        Write-Host "Docker not found — LanguageTool not started. Need service on :8010." -ForegroundColor Yellow
        return
    }
    & (Join-Path $ps1Dir "Start-LanguageTool.ps1") -Detached
    Start-Sleep -Seconds 2
}

function Start-PteWindow {
    param(
        [string]$Title,
        [string]$ScriptName
    )
    $scriptPath = Join-Path $ps1Dir $ScriptName
    $cmd = @"
Set-Location -LiteralPath '$RepoRoot'
`$Host.UI.RawUI.WindowTitle = '$Title'
& '$scriptPath'
"@
    Start-Process -FilePath "powershell.exe" `
        -ArgumentList @("-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $cmd) `
        -WorkingDirectory $RepoRoot | Out-Null
    Write-Host "  + $Title" -ForegroundColor Green
}

function Start-PteBackendBackground {
    $backendDir = Join-Path $RepoRoot "backend"
    $python = Get-PtePythonExe -RepoRoot $RepoRoot
    $storageDir = Join-Path $backendDir "storage"
    if (-not (Test-Path -LiteralPath $storageDir)) {
        New-Item -ItemType Directory -Path $storageDir | Out-Null
    }
    $cmd = "`"$python`" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
    Start-PteBackgroundProcess -Name "backend" -WorkingDirectory $backendDir -CommandLine $cmd -RepoRoot $RepoRoot | Out-Null
    Start-Sleep -Seconds 1
}

function Start-PteFrontendBackground {
    $frontendDir = Join-Path $RepoRoot "frontend"
    $api = $env:VITE_API_BASE_URL
    $cmd = "set VITE_API_BASE_URL=$api&& npm run dev -- --host 127.0.0.1 --port 5173"
    Start-PteBackgroundProcess -Name "frontend" -WorkingDirectory $frontendDir -CommandLine $cmd -RepoRoot $RepoRoot | Out-Null
    Start-Sleep -Seconds 2
}

if ($Background -or $Foreground) {
    Start-PteLanguageTool
    Start-PteBackendBackground

    if ($Foreground) {
        Write-Host ""
        Write-Host "Open: http://127.0.0.1:5173" -ForegroundColor Cyan
        Write-Host "Stop: .\scripts\powershell\Stop-Host.ps1"
        Write-Host ""
        & (Join-Path $ps1Dir "Start-Frontend.ps1")
        exit $LASTEXITCODE
    }

    Start-PteFrontendBackground

    $runtime = Get-PteRuntimeDir -RepoRoot $RepoRoot
    $backendLog = Join-Path $runtime "backend.log"
    $frontendLog = Join-Path $runtime "frontend.log"
    Write-Host ""
    Write-Host "Services started in background:" -ForegroundColor Cyan
    Write-Host "  UI:    http://127.0.0.1:5173"
    Write-Host "  API:   http://127.0.0.1:8000/health"
    Write-Host "  Logs:  $backendLog"
    Write-Host "         $frontendLog"
    Write-Host ""
    Write-Host "Ollama on host: ollama serve" -ForegroundColor DarkYellow
    Write-Host "Check: .\scripts\powershell\Check-Host.ps1"
    Write-Host "Stop:  .\scripts\powershell\Stop-Host.ps1"
    exit 0
}

# Default: separate windows
if (-not $SkipLanguageTool) {
    if (Test-PteCommand "docker") {
        Start-PteWindow -Title "PTE DocEx - LanguageTool :8010" -ScriptName "Start-LanguageTool.ps1"
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Docker not found — LanguageTool not started. Correspondence check needs LT on :8010." -ForegroundColor Yellow
    }
} else {
    Write-Host "LanguageTool skipped (-SkipLanguageTool)." -ForegroundColor DarkYellow
}

Start-PteWindow -Title "PTE DocEx - Backend :8000" -ScriptName "Start-Backend.ps1"
Start-Sleep -Seconds 1
Start-PteWindow -Title "PTE DocEx - Frontend :5173" -ScriptName "Start-Frontend.ps1"

$defaultModel = if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { "llama3.1:8b" }

Write-Host ""
Write-Host "Open:   http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "Health: http://127.0.0.1:8000/health"
Write-Host "Models: http://127.0.0.1:8000/api/learned-lessons/models"
Write-Host ""
Write-Host "Ollama: ollama serve && ollama pull $defaultModel" -ForegroundColor DarkYellow
Write-Host "Check:  .\scripts\powershell\Check-Host.ps1"
Write-Host "Close PowerShell windows or press Ctrl+C in each to stop."
