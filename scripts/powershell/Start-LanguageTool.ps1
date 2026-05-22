# LanguageTool in Docker on port 8010.
#   .\scripts\powershell\Start-LanguageTool.ps1
#   .\scripts\powershell\Start-LanguageTool.ps1 -Detached

param(
    [switch]$Detached,
    [switch]$Help
)

. (Join-Path $PSScriptRoot "_common.ps1")

if ($Help) {
    @"
Usage: Start-LanguageTool.ps1 [-Detached] [-Help]

  -Detached  Run in background (docker compose up -d)
  (default)  Interactive — logs in current window
"@ | Write-Host
    exit 0
}

Assert-PteHostPrereqs -RequireDocker

$RepoRoot = Get-PteRepoRoot

Write-PteHostBanner -Title "LanguageTool - http://127.0.0.1:8010"
if ($Detached) {
    Write-Host "Mode: detached (docker compose up -d)"
} else {
    Write-Host "Stop: Ctrl+C"
}
Write-Host ""

Push-Location $RepoRoot
try {
    $null = & docker compose version 2>$null
    if ($LASTEXITCODE -eq 0) {
        if ($Detached) {
            docker compose up -d languagetool
            Write-Host "LanguageTool started. Logs: docker compose logs -f languagetool" -ForegroundColor Green
        } else {
            docker compose up languagetool
        }
    } elseif ($Detached) {
        docker run -d --rm --name pte-docex-languagetool -p 8010:8010 erikvl87/languagetool:latest
        Write-Host "LanguageTool started (docker run). Stop: docker stop pte-docex-languagetool" -ForegroundColor Green
    } else {
        docker run --rm -p 8010:8010 erikvl87/languagetool:latest
    }
} finally {
    Pop-Location
}
