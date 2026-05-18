# Запуск LanguageTool, backend и frontend в отдельных окнах PowerShell.
#   .\scripts\powershell\Start-Host.ps1
#   .\scripts\powershell\Start-Host.ps1 -SkipLanguageTool   # если LT уже запущен

param(
    [switch]$SkipLanguageTool,
    [switch]$SkipSetupCheck
)

. "$PSScriptRoot\_common.ps1"

$RepoRoot = Get-PteRepoRoot
$ps1Dir = $PSScriptRoot

Write-PteHostBanner -Title "PTE-DocEx — запуск на хосте"

if (-not $SkipSetupCheck) {
    $venvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
    $nodeModules = Join-Path $RepoRoot "frontend\node_modules"
    if (-not ((Test-Path -LiteralPath $venvPython) -and (Test-Path -LiteralPath $nodeModules))) {
        Write-Host "Не найдены backend\.venv или frontend\node_modules. Запуск Setup-Host.ps1 ..." -ForegroundColor Yellow
        & (Join-Path $ps1Dir "Setup-Host.ps1")
    }
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
Write-Host ""
Write-Host "На хосте должен быть запущен Ollama (ollama serve), модель: ollama pull llama3.1:8b" -ForegroundColor DarkYellow
Write-Host "Закройте окна PowerShell или Ctrl+C в каждом для остановки."
