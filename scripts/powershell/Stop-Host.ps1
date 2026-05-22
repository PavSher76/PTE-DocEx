# Stop PTE-DocEx on Windows host (pid files, ports, LanguageTool in Docker).
#   .\scripts\powershell\Stop-Host.ps1

. (Join-Path $PSScriptRoot "_common.ps1")

$RepoRoot = Get-PteRepoRoot
Write-PteHostBanner -Title "Stop PTE-DocEx on host"

Stop-PtePidfile -Name "backend" -RepoRoot $RepoRoot
Stop-PtePidfile -Name "frontend" -RepoRoot $RepoRoot

foreach ($port in @(5173, 8000)) {
    Stop-PtePortListeners -Port $port
}

if (Test-PteCommand "docker") {
    Push-Location $RepoRoot
    try {
        $null = & docker compose version 2>$null
        if ($LASTEXITCODE -eq 0) {
            docker compose stop languagetool 2>$null
        }
        docker stop pte-docex-languagetool 2>$null
    } finally {
        Pop-Location
    }
    Stop-PtePortListeners -Port 8010
}

Write-Host "Done." -ForegroundColor Green
