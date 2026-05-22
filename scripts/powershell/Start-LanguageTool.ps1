# Запуск LanguageTool в Docker на порту 8010.
#   .\scripts\powershell\Start-LanguageTool.ps1
#   .\scripts\powershell\Start-LanguageTool.ps1 -Detached

param(
    [switch]$Detached,
    [switch]$Help
)

. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @"
Использование: Start-LanguageTool.ps1 [-Detached] [-Help]

  -Detached  Запуск в фоне (docker compose up -d)
  (без флага) Интерактивный режим — логи в текущем окне
"@ | Write-Host
    exit 0
}

Assert-PteHostPrereqs -RequireDocker

$RepoRoot = Get-PteRepoRoot

Write-PteHostBanner -Title "LanguageTool — http://127.0.0.1:8010"
if ($Detached) {
    Write-Host "Режим: фоновый (docker compose up -d)"
} else {
    Write-Host "Остановка: Ctrl+C"
}
Write-Host ""

Push-Location $RepoRoot
try {
    $null = & docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        if ($Detached) {
            docker compose up -d languagetool
            Write-Host "LanguageTool запущен. Логи: docker compose logs -f languagetool" -ForegroundColor Green
        } else {
            docker compose up languagetool
        }
    } elseif ($Detached) {
        docker run -d --rm --name pte-docex-languagetool -p 8010:8010 erikvl87/languagetool:latest
        Write-Host "LanguageTool запущен (docker run). Остановка: docker stop pte-docex-languagetool" -ForegroundColor Green
    } else {
        docker run --rm -p 8010:8010 erikvl87/languagetool:latest
    }
} finally {
    Pop-Location
}
