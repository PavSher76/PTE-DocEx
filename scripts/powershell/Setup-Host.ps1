# Установка зависимостей backend (venv + pip) и frontend (npm).
# Запуск из корня репозитория или из этой папки:
#   .\scripts\powershell\Setup-Host.ps1

. "$PSScriptRoot\_common.ps1"

$RepoRoot = Get-PteRepoRoot
Write-PteHostBanner -Title "PTE-DocEx — установка зависимостей на хосте"
Assert-PteHostPrereqs -RequireNode

$backendDir = Join-Path $RepoRoot "backend"
$frontendDir = Join-Path $RepoRoot "frontend"
$venvDir = Join-Path $backendDir ".venv"
$python = Get-Command python -ErrorAction Stop

Write-Host "Репозиторий: $RepoRoot"
Write-Host "Python: $($python.Source)"

if (-not (Test-Path -LiteralPath $venvDir)) {
    Write-Host "Создание venv в backend\.venv ..."
    & $python.Source -m venv $venvDir
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $backendDir "requirements.txt")

$storageDir = Join-Path $backendDir "storage"
if (-not (Test-Path -LiteralPath $storageDir)) {
    New-Item -ItemType Directory -Path $storageDir | Out-Null
}

if (-not (Test-Path -LiteralPath (Join-Path $RepoRoot ".env"))) {
    $hostExample = Join-Path (Join-Path (Split-Path $PSScriptRoot -Parent) "host") "host.env.example"
    if (-not (Test-Path -LiteralPath $hostExample)) {
        $hostExample = Join-Path $PSScriptRoot "host.env.example"
    }
    $example = Join-Path $RepoRoot ".env.example"
    if (Test-Path -LiteralPath $hostExample) {
        Copy-Item -LiteralPath $hostExample -Destination (Join-Path $RepoRoot ".env")
        Write-Host "Создан .env из scripts\host\host.env.example (значения для хоста)." -ForegroundColor Yellow
    } elseif (Test-Path -LiteralPath $example) {
        Copy-Item -LiteralPath $example -Destination (Join-Path $RepoRoot ".env")
        Write-Host "Создан .env из .env.example — для хоста задайте OLLAMA_BASE_URL=http://127.0.0.1:11434 и LANGUAGETOOL_URL=http://127.0.0.1:8010/v2/check" -ForegroundColor Yellow
    }
}

Write-Host "npm install (frontend) ..."
Push-Location $frontendDir
try {
    if (Test-Path -LiteralPath "package-lock.json") {
        npm ci
    } else {
        npm install
    }
} finally {
    Pop-Location
}

Write-Host ""
Write-Host "Готово. Дальше:" -ForegroundColor Green
Write-Host "  1) ollama serve  и  ollama pull llama3.1:8b"
Write-Host "  2) LanguageTool: .\scripts\powershell\Start-LanguageTool.ps1  (нужен Docker)"
Write-Host "  3) .\scripts\powershell\Start-Host.ps1"
Write-Host ""
Write-Host "macOS/Linux: ./scripts/host/setup-host.sh && ./scripts/host/start-host.sh" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Для OCR/сравнения DOCX на Windows установите Tesseract и LibreOffice и добавьте их в PATH." -ForegroundColor DarkYellow
