# LibreOffice, Tesseract и Poppler для OCR / сравнения документов на Windows.
#   .\scripts\powershell\Install-SystemDeps.ps1
#   .\scripts\powershell\Install-SystemDeps.ps1 -WhatIf

param(
    [switch]$WhatIf,
    [switch]$Help
)

. "$PSScriptRoot\_common.ps1"

if ($Help) {
    @"
Использование: Install-SystemDeps.ps1 [-WhatIf] [-Help]

Пробует установить через winget, затем Chocolatey:
  - LibreOffice
  - Tesseract OCR (rus+eng)
  - Poppler (pdftoppm)

После установки добавьте каталоги в PATH и перезапустите PowerShell.
"@ | Write-Host
    exit 0
}

Write-PteHostBanner -Title "Системные зависимости (OCR / LibreOffice)"

function Invoke-PtePackageInstall {
    param(
        [string]$Tool,
        [string[]]$Arguments
    )
    $display = "$Tool $($Arguments -join ' ')"
    if ($WhatIf) {
        Write-Host "[what-if] $display" -ForegroundColor DarkYellow
        return $true
    }
    Write-Host ">> $display"
    & $Tool @Arguments
    return $LASTEXITCODE -eq 0
}

$installed = $false

if (Test-PteCommand "winget") {
    Write-Host "Используется winget..." -ForegroundColor Cyan
    $null = Invoke-PtePackageInstall -Tool "winget" -Arguments @(
        "install", "--id", "TheDocumentFoundation.LibreOffice", "-e",
        "--accept-source-agreements", "--accept-package-agreements"
    )
    $null = Invoke-PtePackageInstall -Tool "winget" -Arguments @(
        "install", "--id", "UB-Mannheim.TesseractOCR", "-e",
        "--accept-source-agreements", "--accept-package-agreements"
    )
    $installed = $true
}

if (Test-PteCommand "choco") {
    Write-Host "Используется Chocolatey..." -ForegroundColor Cyan
    $null = Invoke-PtePackageInstall -Tool "choco" -Arguments @(
        "install", "libreoffice", "tesseract", "poppler", "-y"
    )
    $installed = $true
}

if (-not $installed) {
    Write-Host ""
    Write-Host "winget и Chocolatey не найдены. Установите вручную:" -ForegroundColor Yellow
    Write-Host "  LibreOffice: https://www.libreoffice.org/download/download/"
    Write-Host "  Tesseract:   https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "  Poppler:     https://github.com/oschwartz10612/poppler-windows/releases"
    Write-Host ""
    Write-Host "Типичные пути PATH:"
    Write-Host '  C:\Program Files\LibreOffice\program'
    Write-Host '  C:\Program Files\Tesseract-OCR'
    exit 1
}

Write-Host ""
Write-Host "Проверьте команды в новом окне PowerShell:" -ForegroundColor Green
Write-Host "  tesseract --version"
Write-Host "  soffice --version"
Write-Host "  pdftoppm -h"
