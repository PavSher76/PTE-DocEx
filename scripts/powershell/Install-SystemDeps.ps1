# LibreOffice, Tesseract, Poppler for OCR / document compare on Windows.
#   .\scripts\powershell\Install-SystemDeps.ps1
#   .\scripts\powershell\Install-SystemDeps.ps1 -WhatIf

param(
    [switch]$WhatIf,
    [switch]$Help
)

. (Join-Path $PSScriptRoot "_common.ps1")

if ($Help) {
    @"
Usage: Install-SystemDeps.ps1 [-WhatIf] [-Help]

Tries winget first, then Chocolatey:
  - LibreOffice
  - Tesseract OCR (rus+eng)
  - Poppler (pdftoppm)

After install, add install dirs to PATH and restart PowerShell.
"@ | Write-Host
    exit 0
}

Write-PteHostBanner -Title "System dependencies (OCR / LibreOffice)"

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
    Write-Host "Using winget..." -ForegroundColor Cyan
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
    Write-Host "Using Chocolatey..." -ForegroundColor Cyan
    $null = Invoke-PtePackageInstall -Tool "choco" -Arguments @(
        "install", "libreoffice", "tesseract", "poppler", "-y"
    )
    $installed = $true
}

if (-not $installed) {
    Write-Host ""
    Write-Host "winget and Chocolatey not found. Install manually:" -ForegroundColor Yellow
    Write-Host "  LibreOffice: https://www.libreoffice.org/download/download/"
    Write-Host "  Tesseract:   https://github.com/UB-Mannheim/tesseract/wiki"
    Write-Host "  Poppler:     https://github.com/oschwartz10612/poppler-windows/releases"
    Write-Host ""
    Write-Host "Typical PATH entries:"
    Write-Host '  C:\Program Files\LibreOffice\program'
    Write-Host '  C:\Program Files\Tesseract-OCR'
    exit 1
}

Write-Host ""
Write-Host "Verify in a new PowerShell window:" -ForegroundColor Green
Write-Host "  tesseract --version"
Write-Host "  soffice --version"
Write-Host "  pdftoppm -h"
