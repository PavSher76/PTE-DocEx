# Backend (FastAPI / uvicorn) at http://127.0.0.1:8000
#   .\scripts\powershell\Start-Backend.ps1

. (Join-Path $PSScriptRoot "_common.ps1")

$RepoRoot = Get-PteRepoRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

$backendDir = Join-Path $RepoRoot "backend"
$python = Get-PtePythonExe -RepoRoot $RepoRoot
$storageDir = Join-Path $backendDir "storage"
if (-not (Test-Path -LiteralPath $storageDir)) {
    New-Item -ItemType Directory -Path $storageDir | Out-Null
}

Write-PteHostBanner -Title "Backend - http://127.0.0.1:8000"
Write-Host "LanguageTool: $env:LANGUAGETOOL_URL"
Write-Host "Ollama:       $env:OLLAMA_BASE_URL"
Write-Host "Database:     $env:DATABASE_URL"
Write-Host "Stop: Ctrl+C"
Write-Host ""

Push-Location $backendDir
try {
    & $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
} finally {
    Pop-Location
}
