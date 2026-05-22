# Check local Windows host environment readiness.
#   .\scripts\powershell\Check-Host.ps1

. (Join-Path $PSScriptRoot "_common.ps1")

$RepoRoot = Get-PteRepoRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

Write-PteHostBanner -Title "PTE-DocEx environment check"

function Write-PteOk { param([string]$Message) Write-Host "  [ok] $Message" -ForegroundColor Green }
function Write-PteWarn { param([string]$Message) Write-Host "  [!!] $Message" -ForegroundColor Yellow }
function Write-PteFail { param([string]$Message) Write-Host "  [xx] $Message" -ForegroundColor Red }

if ((Test-PteCommand "python") -or (Test-PteCommand "py")) {
    $py = if (Test-PteCommand "python") { (Get-Command python).Source } else { "py -3" }
    Write-PteOk "python: $py"
} else {
    Write-PteFail "python not found"
}

if (Test-PteCommand "npm") {
    Write-PteOk "npm: $((Get-Command npm).Source)"
} else {
    Write-PteFail "npm not found"
}

$venvPython = Get-PteVenvPythonPath -RepoRoot $RepoRoot
if (Test-Path -LiteralPath $venvPython) {
    Write-PteOk "backend/.venv"
} else {
    Write-PteWarn "missing backend/.venv — run Setup-Host.ps1"
}

$nodeModules = Join-PtePath $RepoRoot @("frontend", "node_modules")
if (Test-Path -LiteralPath $nodeModules) {
    Write-PteOk "frontend/node_modules"
} else {
    Write-PteWarn "missing node_modules — run Setup-Host.ps1"
}

$dotenv = Join-Path $RepoRoot ".env"
if (Test-Path -LiteralPath $dotenv) {
    Write-PteOk ".env"
} else {
    Write-PteWarn "missing .env — created by Setup-Host.ps1"
}

$ollamaUrl = "$($env:OLLAMA_BASE_URL.TrimEnd('/'))/api/tags"
if (Test-PteHttpOk -Url $ollamaUrl) {
    Write-PteOk "Ollama $env:OLLAMA_BASE_URL"
    try {
        $models = Invoke-RestMethod -Uri $ollamaUrl -TimeoutSec 3
        $count = @($models.models).Count
        Write-PteOk "Ollama models: $count"
    } catch {
        Write-PteWarn "Ollama responded but model list could not be parsed"
    }
} else {
    Write-PteWarn "Ollama unreachable ($env:OLLAMA_BASE_URL) — run: ollama serve"
}

$ltBase = $env:LANGUAGETOOL_URL -replace "/v2/check$", ""
if (Test-PteHttpOk -Url "$ltBase/v2/languages") {
    Write-PteOk "LanguageTool $ltBase"
} else {
    Write-PteWarn "LanguageTool unreachable — Start-LanguageTool.ps1 or docker compose up -d languagetool"
}

if (Test-PteHttpOk -Url "http://127.0.0.1:8000/health") {
    Write-PteOk "Backend http://127.0.0.1:8000/health"
} else {
    Write-PteWarn "Backend not responding on :8000"
}

if (Test-PteHttpOk -Url "http://127.0.0.1:5173") {
    Write-PteOk "Frontend http://127.0.0.1:5173"
} else {
    Write-PteWarn "Frontend not responding on :5173"
}

if ($env:RAG_ENABLED -eq "true") {
    if (Test-PteHttpOk -Url "$($env:RAG_API_URL.TrimEnd('/'))/health") {
        Write-PteOk "RAG API $env:RAG_API_URL"
    } else {
        Write-PteWarn "RAG API unreachable ($env:RAG_API_URL) — docker compose up rag-api"
    }
}

foreach ($cmd in @("tesseract", "soffice", "pdftoppm")) {
    if (Test-PteCommand $cmd) {
        Write-PteOk $cmd
    } else {
        Write-PteWarn "$cmd not in PATH (OCR/DOCX) — Install-SystemDeps.ps1"
    }
}

Write-Host ""
