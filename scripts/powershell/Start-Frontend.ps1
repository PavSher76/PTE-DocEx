# Frontend (Vite) на http://127.0.0.1:5173
# API указывается на backend хоста (обход docker-прокси vite.config).
#   .\scripts\powershell\Start-Frontend.ps1

. "$PSScriptRoot\_common.ps1"

$RepoRoot = Get-PteRepoRoot
$frontendDir = Join-Path $RepoRoot "frontend"

if (-not $env:VITE_API_BASE_URL) {
    $env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
}

Assert-PteHostPrereqs -RequireNode

Write-PteHostBanner -Title "Frontend — http://127.0.0.1:5173"
Write-Host "VITE_API_BASE_URL = $env:VITE_API_BASE_URL"
Write-Host "Остановка: Ctrl+C"
Write-Host ""

Push-Location $frontendDir
try {
    npm run dev -- --host 127.0.0.1 --port 5173
} finally {
    Pop-Location
}
