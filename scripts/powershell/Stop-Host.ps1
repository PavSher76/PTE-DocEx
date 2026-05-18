# Остановка процессов, слушающих порты PTE-DocEx (5173, 8000, 8010).
# Требуются права на Get-NetTCPConnection (обычно есть у пользователя).
#   .\scripts\powershell\Stop-Host.ps1

$ErrorActionPreference = "SilentlyContinue"
$ports = @(5173, 8000, 8010)

Write-Host "Остановка слушателей на портах: $($ports -join ', ')" -ForegroundColor Cyan

foreach ($port in $ports) {
    $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
    if (-not $conns) {
        Write-Host "  :$port — нет слушателя"
        continue
    }
    $pids = $conns.OwningProcess | Sort-Object -Unique
    foreach ($procId in $pids) {
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        $name = if ($proc) { $proc.ProcessName } else { "?" }
        Write-Host "  :$port — завершение PID $procId ($name)"
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "Готово."
