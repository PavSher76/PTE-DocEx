# Проверка готовности локального окружения Windows.
#   .\scripts\powershell\Check-Host.ps1

. "$PSScriptRoot\_common.ps1"

$RepoRoot = Get-PteRepoRoot
Set-PteHostDefaults -RepoRoot $RepoRoot

Write-PteHostBanner -Title "Проверка окружения PTE-DocEx"

function Write-PteOk { param([string]$Message) Write-Host "  [ok] $Message" -ForegroundColor Green }
function Write-PteWarn { param([string]$Message) Write-Host "  [!!] $Message" -ForegroundColor Yellow }
function Write-PteFail { param([string]$Message) Write-Host "  [xx] $Message" -ForegroundColor Red }

if ((Test-PteCommand "python") -or (Test-PteCommand "py")) {
    $py = if (Test-PteCommand "python") { (Get-Command python).Source } else { "py -3" }
    Write-PteOk "python: $py"
} else {
    Write-PteFail "python не найден"
}

if (Test-PteCommand "npm") {
    Write-PteOk "npm: $((Get-Command npm).Source)"
} else {
    Write-PteFail "npm не найден"
}

$venvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
if (Test-Path -LiteralPath $venvPython) {
    Write-PteOk "backend\.venv"
} else {
    Write-PteWarn "нет backend\.venv — выполните Setup-Host.ps1"
}

if (Test-Path -LiteralPath (Join-Path $RepoRoot "frontend\node_modules")) {
    Write-PteOk "frontend\node_modules"
} else {
    Write-PteWarn "нет node_modules — выполните Setup-Host.ps1"
}

if (Test-Path -LiteralPath (Join-Path $RepoRoot ".env")) {
    Write-PteOk ".env"
} else {
    Write-PteWarn "нет .env — будет создан при Setup-Host.ps1"
}

$ollamaUrl = "$($env:OLLAMA_BASE_URL.TrimEnd('/'))/api/tags"
if (Test-PteHttpOk -Url $ollamaUrl) {
    Write-PteOk "Ollama $env:OLLAMA_BASE_URL"
    try {
        $models = Invoke-RestMethod -Uri $ollamaUrl -TimeoutSec 3
        $count = @($models.models).Count
        Write-PteOk "Ollama models: $count"
    } catch {
        Write-PteWarn "Ollama ответила, но список моделей не разобран"
    }
} else {
    Write-PteWarn "Ollama недоступна ($env:OLLAMA_BASE_URL) — выполните: ollama serve"
}

$ltBase = $env:LANGUAGETOOL_URL -replace "/v2/check$", ""
if (Test-PteHttpOk -Url "$ltBase/v2/languages") {
    Write-PteOk "LanguageTool $ltBase"
} else {
    Write-PteWarn "LanguageTool недоступен — Start-LanguageTool.ps1 или docker compose up -d languagetool"
}

if (Test-PteHttpOk -Url "http://127.0.0.1:8000/health") {
    Write-PteOk "Backend http://127.0.0.1:8000/health"
} else {
    Write-PteWarn "Backend не отвечает на :8000"
}

if (Test-PteHttpOk -Url "http://127.0.0.1:5173") {
    Write-PteOk "Frontend http://127.0.0.1:5173"
} else {
    Write-PteWarn "Frontend не отвечает на :5173"
}

if ($env:RAG_ENABLED -eq "true") {
    if (Test-PteHttpOk -Url "$($env:RAG_API_URL.TrimEnd('/'))/health") {
        Write-PteOk "RAG API $env:RAG_API_URL"
    } else {
        Write-PteWarn "RAG API недоступен ($env:RAG_API_URL) — docker compose up rag-api"
    }
}

foreach ($cmd in @("tesseract", "soffice", "pdftoppm")) {
    if (Test-PteCommand $cmd) {
        Write-PteOk $cmd
    } else {
        Write-PteWarn "$cmd не в PATH (OCR/сравнение DOCX) — Install-SystemDeps.ps1"
    }
}

Write-Host ""
