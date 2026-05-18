# LanguageTool в Docker на порту 8010 (как в docker-compose).
#   .\scripts\powershell\Start-LanguageTool.ps1

. "$PSScriptRoot\_common.ps1"

Assert-PteHostPrereqs -RequireDocker

Write-PteHostBanner -Title "LanguageTool (Docker, :8010)"
Write-Host "Остановка: Ctrl+C"
Write-Host ""

docker run --rm -p 8010:8010 erikvl87/languagetool:latest
