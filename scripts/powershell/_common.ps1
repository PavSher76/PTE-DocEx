# Общие функции для скриптов PTE-DocEx (запуск на хосте Windows).
# Подключение: . "$PSScriptRoot\_common.ps1"

$ErrorActionPreference = "Stop"

function Get-PteRepoRoot {
    $root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
    return $root.Path
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

function Set-PteHostDefaults {
    param([string]$RepoRoot)

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
}

function Get-PtePythonExe {
    param([string]$RepoRoot)

    $venvPython = Join-Path $RepoRoot "backend\.venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPython) {
        return $venvPython
    }
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
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
    if (-not (Test-PteCommand "python")) {
        throw "В PATH нет python. Установите Python 3.12+ с https://www.python.org/downloads/"
    }
    if ($RequireNode -and -not (Test-PteCommand "npm")) {
        throw "В PATH нет npm. Установите Node.js LTS с https://nodejs.org/"
    }
    if ($RequireDocker -and -not (Test-PteCommand "docker")) {
        throw "В PATH нет docker. Установите Docker Desktop или запустите LanguageTool вручную на порту 8010."
    }
}
