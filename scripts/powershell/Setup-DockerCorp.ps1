# Configure .env for Docker on corporate Windows (proxy IP + DNS for containers).
#   .\scripts\powershell\Setup-DockerCorp.ps1
#   .\scripts\powershell\Setup-DockerCorp.ps1 -Apply
#
# After -Apply, start stack:
#   docker compose -f docker-compose.yml -f docker-compose.corp-windows.yml up --build

param(
    [switch]$Apply,
    [switch]$Help
)

. (Join-Path $PSScriptRoot "_common.ps1")

if ($Help) {
    @"
Usage: Setup-DockerCorp.ps1 [-Apply] [-Help]

Reads HTTP_PROXY from .env, resolves proxy hostname to IP (nslookup),
detects host DNS (Get-DnsClientServerAddress), and prints recommended .env values.

  -Apply  Write CORP_DNS, CORP_PROXY_* and IP-based HTTP_PROXY into .env
  -Help   Show this help

Start stack after -Apply:
  docker compose -f docker-compose.yml -f docker-compose.corp-windows.yml up --build
"@ | Write-Host
    exit 0
}

function Get-PteEnvValue {
    param([string]$Name, [hashtable]$Vars)
    if ($Vars.ContainsKey($Name)) { return $Vars[$Name] }
    return $null
}

function Set-PteEnvValue {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Lines,
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Value
    )
    $pattern = "^\s*$([regex]::Escape($Name))\s*="
    $replacement = "$Name=$Value"
    $updated = $false
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match $pattern) {
            $Lines[$i] = $replacement
            $updated = $true
            break
        }
    }
    if (-not $updated) {
        $Lines += $replacement
    }
    return ,$Lines
}

function Read-PteEnvLines {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return @()
    }
    return @(Get-Content -LiteralPath $Path -Encoding UTF8)
}

function Get-PteEnvMap {
    param([string[]]$Lines)
    $map = @{}
    foreach ($line in $Lines) {
        $trim = $line.Trim()
        if ($trim.Length -eq 0 -or $trim.StartsWith("#")) { continue }
        $eq = $trim.IndexOf("=")
        if ($eq -lt 1) { continue }
        $name = $trim.Substring(0, $eq).Trim()
        $value = $trim.Substring($eq + 1).Trim()
        $map[$name] = $value
    }
    return $map
}

function Get-ProxyHostFromUrl {
    param([string]$Url)
    if (-not $Url) { return $null }
    try {
        $uri = [Uri]$Url
        return $uri.Host
    } catch {
        return $null
    }
}

function Test-Ipv4Address {
    param([string]$HostName)
    return [bool]([System.Net.IPAddress]::TryParse($HostName, [ref]([System.Net.IPAddress]::None)))
}

function Resolve-PteHostAddress {
    param([string]$HostName)
    if (-not $HostName) { return $null }
    if (Test-Ipv4Address $HostName) { return $HostName }
    try {
        $result = Resolve-DnsName -Name $HostName -Type A -ErrorAction Stop |
            Where-Object { $_.Type -eq "A" } |
            Select-Object -First 1
        if ($result) { return $result.IPAddress }
    } catch {
        try {
            $ns = nslookup $HostName 2>$null | Select-String -Pattern "Address(?:es)?:\s*(\d+\.\d+\.\d+\.\d+)" -AllMatches
            foreach ($match in $ns.Matches) {
                $ip = $match.Groups[1].Value
                if ($ip -and $ip -notmatch "^(127\.|0\.)") { return $ip }
            }
        } catch { }
    }
    return $null
}

function Get-PtePrimaryDns {
    $servers = Get-DnsClientServerAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.ServerAddresses -and $_.ServerAddresses.Count -gt 0 } |
        Sort-Object -Property InterfaceMetric |
        Select-Object -First 1
    if ($servers -and $servers.ServerAddresses.Count -gt 0) {
        return $servers.ServerAddresses[0]
    }
    return "10.0.0.1"
}

function Set-ProxyUrlHost {
    param(
        [string]$Url,
        [string]$NewHost
    )
    if (-not $Url) { return $null }
    $uri = [Uri]$Url
    $builder = New-Object System.UriBuilder $uri
    $builder.Host = $NewHost
    return $builder.Uri.ToString().TrimEnd("/")
}

$RepoRoot = Get-PteRepoRoot
Ensure-PteDotenv -RepoRoot $RepoRoot
$envPath = Join-Path $RepoRoot ".env"
$lines = Read-PteEnvLines -Path $envPath
$envMap = Get-PteEnvMap -Lines $lines

$proxyUrl = Get-PteEnvValue -Name "HTTP_PROXY" -Vars $envMap
if (-not $proxyUrl) {
    $proxyUrl = Get-PteEnvValue -Name "HTTPS_PROXY" -Vars $envMap
}
if (-not $proxyUrl) {
    throw "HTTP_PROXY is not set in .env. Copy docker/proxy.env.example and set your corporate proxy URL."
}

$proxyHost = Get-ProxyHostFromUrl -Url $proxyUrl
$proxyIp = Resolve-PteHostAddress -HostName $proxyHost
if (-not $proxyIp) {
    throw "Cannot resolve proxy host '$proxyHost' on Windows. Check VPN and run: nslookup $proxyHost"
}

$corpDns = Get-PtePrimaryDns
$httpProxyIp = Set-ProxyUrlHost -Url $proxyUrl -NewHost $proxyIp
$httpsSource = Get-PteEnvValue -Name "HTTPS_PROXY" -Vars $envMap
if (-not $httpsSource) { $httpsSource = $proxyUrl }
$httpsProxyIp = Set-ProxyUrlHost -Url $httpsSource -NewHost $proxyIp

Write-PteHostBanner -Title "PTE-DocEx — Docker corporate Windows"
Write-Host "Proxy host (from .env): $proxyHost"
Write-Host "Proxy IP (resolved):    $proxyIp"
Write-Host "Host DNS for containers: $corpDns"
Write-Host ""
Write-Host "Recommended .env:" -ForegroundColor Cyan
Write-Host "  HTTP_PROXY=$httpProxyIp"
Write-Host "  HTTPS_PROXY=$httpsProxyIp"
Write-Host "  CORP_DNS=$corpDns"
Write-Host "  CORP_PROXY_HOST=$proxyHost"
Write-Host "  CORP_PROXY_IP=$proxyIp"
Write-Host ""
Write-Host "Docker Desktop -> Settings -> Docker Engine -> set:" -ForegroundColor Cyan
Write-Host @"
  `"dns`": [`"$corpDns`"],
  `"proxies`": {
    `"default`": {
      `"httpProxy`": `"$httpProxyIp`",
      `"httpsProxy`": `"$httpsProxyIp`",
      `"noProxy`": `"localhost,127.0.0.1,host.docker.internal,.local,.eurochem.ru,.tgp.eurochem.ru,.usl.eurochem.ru`"
    }
  }
"@
Write-Host ""
Write-Host "Start command:" -ForegroundColor Green
Write-Host "  docker compose -f docker-compose.yml -f docker-compose.corp-windows.yml up --build"

if ($Apply) {
    $lines = Set-PteEnvValue -Lines $lines -Name "HTTP_PROXY" -Value $httpProxyIp
    $lines = Set-PteEnvValue -Lines $lines -Name "HTTPS_PROXY" -Value $httpsProxyIp
    $lines = Set-PteEnvValue -Lines $lines -Name "CORP_DNS" -Value $corpDns
    $lines = Set-PteEnvValue -Lines $lines -Name "CORP_PROXY_HOST" -Value $proxyHost
    $lines = Set-PteEnvValue -Lines $lines -Name "CORP_PROXY_IP" -Value $proxyIp
    if (-not (Get-PteEnvValue -Name "SKIP_APT_PACKAGES" -Vars $envMap)) {
        $lines = Set-PteEnvValue -Lines $lines -Name "SKIP_APT_PACKAGES" -Value "1"
    }
    Set-Content -LiteralPath $envPath -Value $lines -Encoding UTF8
    Write-Host ""
    Write-Host "Updated $envPath" -ForegroundColor Green
}
