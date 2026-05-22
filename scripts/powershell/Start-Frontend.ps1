# Frontend (Vite) at http://127.0.0.1:5173
# API points to host backend (not Docker vite proxy).
#   .\scripts\powershell\Start-Frontend.ps1

. (Join-Path $PSScriptRoot "_common.ps1")

$RepoRoot = Get-PteRepoRoot
Set-PteHostDefaults -RepoRoot $RepoRoot
$frontendDir = Join-Path $RepoRoot "frontend"

Assert-PteHostPrereqs -RequireNode

Write-PteHostBanner -Title "Frontend - http://127.0.0.1:5173"
Write-Host "VITE_API_BASE_URL = $env:VITE_API_BASE_URL"
Write-Host "Stop: Ctrl+C"
Write-Host ""

Push-Location $frontendDir
try {
    npm run dev -- --host 127.0.0.1 --port 5173
} finally {
    Pop-Location
}
