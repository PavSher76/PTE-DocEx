# Общие функции для скриптов PTE-DocEx (запуск на хосте Windows).
# Подключение: . "$PSScriptRoot\_common.ps1"

$ErrorActionPreference = "Stop"

function Get-PteRepoRoot {
    $root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    return $root.Path
}

function Get-PteRuntimeDir {
    param([string]$RepoRoot = (Get-PteRepoRoot))
    $dir = Join-Path $RepoRoot ".pte-host"
    if (-not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }
    return $dir
}

function Get-PteHostEnvExamplePath {
    $fromHost = Join-Path (Join-Path (Split-Path $PSScriptRoot -Parent) "host") "host.env.example"
    if (Test-Path -LiteralPath $fromHost) {
        return $fromHost
    }
    return Join-Path $PSScriptRoot "host.env.example"
}

function Import-PteEnvFile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }
    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line.Length -eq 0 -or $line.StartsWith("#")) {
            return
        }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) {
            return
        }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

function Ensure-PteDotenv {
    param([string]$RepoRoot = (Get-PteRepoRoot))

    $target = Join-Path $RepoRoot ".env"
    if (Test-Path -LiteralPath $target) {
        return
    }

    $hostExample = Get-PteHostEnvExamplePath
    $rootExample = Join-Path $RepoRoot ".env.example"
    if (Test-Path -LiteralPath $hostExample) {
        Copy-Item -LiteralPath $hostExample -Destination $target
        Write-Host "Создан .env из $(Split-Path $hostExample -Leaf) (значения для хоста)." -ForegroundColor Yellow
    } elseif (Test-Path -LiteralPath $rootExample) {
        Copy-Item -LiteralPath $rootExample -Destination $target
        Write-Host "Создан .env из .env.example — для хоста задайте OLLAMA_BASE_URL=http://127.0.0.1:11434" -ForegroundColor Yellow
    }
}

function Set-PteHostDefaults {
    param([string]$RepoRoot = (Get-PteRepoRoot))

    Ensure-PteDotenv -RepoRoot $RepoRoot
    Import-PteEnvFile -Path (Join-Path $RepoRoot ".env")

    if (-not $env:DATABASE_URL) {
        $env:DATABASE_URL = "sqlite:///./storage/app.db"
    }
    if (-not $env:LANGUAGETOOL_URL) {
        $env:LANGUAGETOOL_URL = "http://127.0.0.1:8010/v2/check"
    }
    if (-not $env:OLLAMA_BASE_URL) {
        $env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
    }
    if (-not $env:OLLAMA_MODEL) {
        $env:OLLAMA_MODEL = "llama3.1:8b"
    }
    if (-not $env:OLLAMA_TIMEOUT_SECONDS) {
        $env:OLLAMA_TIMEOUT_SECONDS = "180"
    }
    if (-not $env:VITE_API_BASE_URL) {
        $env:VITE_API_BASE_URL = "http://127.0.0.1:8000"
    }
    if (-not $env:RAG_ENABLED) {
        $env:RAG_ENABLED = "true"
    }
    if (-not $env:RAG_API_URL) {
        $env:RAG_API_URL = "http://127.0.0.1:8100"
    }
}

function Get-PtePythonExe {
    param([string]$RepoRoot = (Get-PteRepoRoot))

    $venvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }
    foreach ($name in @("python", "python3", "py")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) {
            return $cmd.Source
        }
    }
    throw "Python не найден. Выполните scripts\powershell\Setup-Host.ps1 или установите Python 3.12+."
}

function Test-PteCommand {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Write-PteHostBanner {
    param([string]$Title)
    Write-Host ""
    Write-Host "=== $Title ===" -ForegroundColor Cyan
}

function Assert-PteHostPrereqs {
    param(
        [switch]$RequireNode,
        [switch]$RequireDocker
    )
    $hasPython = (Test-PteCommand "python") -or (Test-PteCommand "python3") -or (Test-PteCommand "py")
    if (-not $hasPython) {
        throw "В PATH нет python. Установите Python 3.12+ с https://www.python.org/downloads/ (галочка Add to PATH)."
    }
    if ($RequireNode -and -not (Test-PteCommand "npm")) {
        throw "В PATH нет npm. Установите Node.js LTS (22+) с https://nodejs.org/"
    }
    if ($RequireDocker -and -not (Test-PteCommand "docker")) {
        throw "В PATH нет docker. Установите Docker Desktop или поднимите LanguageTool на порту 8010 вручную."
    }
}

function Write-PtePid {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,
        [string]$RepoRoot = (Get-PteRepoRoot)
    )
    $file = Join-Path (Get-PteRuntimeDir -RepoRoot $RepoRoot) "$Name.pid"
    Set-Content -LiteralPath $file -Value $ProcessId -Encoding ASCII
}

function Read-PtePid {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [string]$RepoRoot = (Get-PteRepoRoot)
    )
    $file = Join-Path (Get-PteRuntimeDir -RepoRoot $RepoRoot) "$Name.pid"
    if (-not (Test-Path -LiteralPath $file)) {
        return $null
    }
    $raw = (Get-Content -LiteralPath $file -Raw).Trim()
    if (-not $raw) {
        return $null
    }
    $processId = [int]$raw
    if (Get-Process -Id $processId -ErrorAction SilentlyContinue) {
        return $processId
    }
    Remove-Item -LiteralPath $file -Force -ErrorAction SilentlyContinue
    return $null
}

function Stop-PtePidfile {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [string]$RepoRoot = (Get-PteRepoRoot)
    )
    $processId = Read-PtePid -Name $Name -RepoRoot $RepoRoot
    if (-not $processId) {
        return
    }
    Write-Host "  остановка $Name (PID $processId)"
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    $file = Join-Path (Get-PteRuntimeDir -RepoRoot $RepoRoot) "$Name.pid"
    Remove-Item -LiteralPath $file -Force -ErrorAction SilentlyContinue
}

function Stop-PtePortListeners {
    param([Parameter(Mandatory = $true)][int]$Port)

    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "  :$Port — нет слушателя"
        return
    }
    $pids = $conns.OwningProcess | Sort-Object -Unique
    foreach ($processId in $pids) {
        $proc = Get-Process -Id $processId -ErrorAction SilentlyContinue
        $name = if ($proc) { $proc.ProcessName } else { "?" }
        Write-Host "  :$Port — завершение PID $processId ($name)"
        Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    }
}

function Test-PteHttpOk {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [int]$TimeoutSec = 2
    )
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec
        return $response.StatusCode -ge 200 -and $response.StatusCode -lt 400
    } catch {
        return $false
    }
}

function Start-PteBackgroundProcess {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory = $true)]
        [string]$CommandLine,
        [string]$RepoRoot = (Get-PteRepoRoot)
    )

    $existing = Read-PtePid -Name $Name -RepoRoot $RepoRoot
    if ($existing) {
        Write-Host "  $Name уже запущен (PID $existing)" -ForegroundColor DarkYellow
        return $existing
    }

    $runtime = Get-PteRuntimeDir -RepoRoot $RepoRoot
    $log = Join-Path $runtime "$Name.log"
    $escapedCmd = $CommandLine.Replace('"', '\"')
    $proc = Start-Process -FilePath "cmd.exe" `
        -ArgumentList @("/c", "$escapedCmd >> `"$log`" 2>&1") `
        -WorkingDirectory $WorkingDirectory `
        -WindowStyle Hidden `
        -PassThru
    Write-PtePid -Name $Name -ProcessId $proc.Id -RepoRoot $RepoRoot
    Write-Host "  + $Name (PID $($proc.Id), лог: $log)" -ForegroundColor Green
    return $proc.Id
}
