# LanguageTool в Docker на порту 8010 (как в docker-compose).
#   .\scripts\powershell\Start-LanguageTool.ps1

. "$PSScriptRoot\_common.ps1"

Assert-PteHostPrereqs -RequireDocker

$RepoRoot = Get-PteRepoRoot

Write-PteHostBanner -Title "LanguageTool (Docker, :8010)"
Write-Host "Остановка: Ctrl+C (docker compose) или docker stop pte-docex-languagetool"
Write-Host ""

Push-Location $RepoRoot
try {
    $compose = Get-Command docker -ErrorAction Stop
    $null = & docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        docker compose up languagetool
    } else {
        docker run --rm -p 8010:8010 erikvl87/languagetool:latest
    }
} finally {
    Pop-Location
}
