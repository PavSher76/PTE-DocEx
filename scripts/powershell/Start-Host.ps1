# Запуск LanguageTool, backend и frontend на хосте Windows.
#
# Отдельные окна PowerShell (по умолчанию):
#   .\scripts\powershell\Start-Host.ps1
#
# Фоновый режим (логи в .pte-host\):
#   .\scripts\powershell\Start-Host.ps1 -Background
#
# Frontend в текущем окне:
#   .\scripts\powershell\Start-Host.ps1 -Foreground

param(
    [switch]$SkipLanguageTool,
    [switch]$SkipSetupCheck,
    [switch]$Background,
    [switch]$Foreground,
    [switch]$Help
)

. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @"
Использование: Start-Host.ps1 [опции]

  (без флагов)       LanguageTool, backend и frontend в отдельных окнах PowerShell
  -Background        Все сервисы в фоне, логи: .pte-host\backend.log, frontend.log
  -Foreground        LT и backend в фоне, frontend в текущем окне
  -SkipLanguageTool  Не запускать LanguageTool
  -SkipSetupCheck    Не вызывать Setup-Host при отсутствии venv/node_modules
  -Help              Эта справка

Требуется Ollama на хосте: ollama serve && ollama pull llama3.1:8b
"@ | Write-Host
    exit 0
}

if ($Background -and $Foreground) {
    throw "Укажите только один режим: -Background или -Foreground."
}

$RepoRoot = Get-PteRepoRoot
$ps1Dir = $PSScriptRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

Write-PteHostBanner -Title "PTE-DocEx — запуск на хосте (Windows)"

if (-not $SkipSetupCheck) {
    $venvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
    $nodeModules = Join-Path $RepoRoot "frontend\node_modules"
    if (-not ((Test-Path -LiteralPath $venvPython) -and (Test-Path -LiteralPath $nodeModules))) {
        Write-Host "Не найдены backend\.venv или frontend\node_modules. Запуск Setup-Host.ps1 ..." -ForegroundColor Yellow
        & (Join-Path $ps1Dir "Setup-Host.ps1")
    }
}

function Start-PteLanguageTool {
    if ($SkipLanguageTool) {
        Write-Host "LanguageTool пропущен (-SkipLanguageTool)." -ForegroundColor DarkYellow
        return
    }
    if (-not (Test-PteCommand "docker")) {
        Write-Host "Docker не найден — LanguageTool не запущен. Нужен сервис на :8010." -ForegroundColor Yellow
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
        Write-Host "Откройте: http://127.0.0.1:5173" -ForegroundColor Cyan
        Write-Host "Остановка: .\scripts\powershell\Stop-Host.ps1"
        Write-Host ""
        & (Join-Path $ps1Dir "Start-Frontend.ps1")
        exit $LASTEXITCODE
    }

    Start-PteFrontendBackground

    $runtime = Get-PteRuntimeDir -RepoRoot $RepoRoot
    Write-Host ""
    Write-Host "Сервисы запущены в фоне:" -ForegroundColor Cyan
    Write-Host "  UI:    http://127.0.0.1:5173"
    Write-Host "  API:   http://127.0.0.1:8000/health"
    Write-Host "  Логи:  $runtime\backend.log  $runtime\frontend.log"
    Write-Host ""
    Write-Host "Ollama на хосте: ollama serve" -ForegroundColor DarkYellow
    Write-Host "Проверка: .\scripts\powershell\Check-Host.ps1"
    Write-Host "Остановка: .\scripts\powershell\Stop-Host.ps1"
    exit 0
}

# Режим по умолчанию: отдельные окна
if (-not $SkipLanguageTool) {
    if (Test-PteCommand "docker") {
        Start-PteWindow -Title "PTE DocEx — LanguageTool :8010" -ScriptName "Start-LanguageTool.ps1"
        Start-Sleep -Seconds 2
    } else {
        Write-Host "Docker не найден — LanguageTool не запущен. Проверка переписки потребует LT на :8010." -ForegroundColor Yellow
    }
} else {
    Write-Host "LanguageTool пропущен (-SkipLanguageTool)." -ForegroundColor DarkYellow
}

Start-PteWindow -Title "PTE DocEx — Backend :8000" -ScriptName "Start-Backend.ps1"
Start-Sleep -Seconds 1
Start-PteWindow -Title "PTE DocEx — Frontend :5173" -ScriptName "Start-Frontend.ps1"

Write-Host ""
Write-Host "Откройте: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "Health:   http://127.0.0.1:8000/health"
Write-Host "Models:   http://127.0.0.1:8000/api/learned-lessons/models"
Write-Host ""
Write-Host "Ollama: ollama serve && ollama pull $(if ($env:OLLAMA_MODEL) { $env:OLLAMA_MODEL } else { 'llama3.1:8b' })" -ForegroundColor DarkYellow
Write-Host "Проверка: .\scripts\powershell\Check-Host.ps1"
Write-Host "Закройте окна PowerShell или Ctrl+C в каждом для остановки."
