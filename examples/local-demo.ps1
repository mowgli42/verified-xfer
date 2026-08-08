#requires -Version 5.1
<#
.SYNOPSIS
  End-to-end local demo (LocalBackend) using four temporary folders.
  Mirrors examples/local-demo.sh for Windows PowerShell operators.
#>
$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Demo = Join-Path ([System.IO.Path]::GetTempPath()) ("verified-xfer-demo-" + [guid]::NewGuid().ToString('N'))
Write-Host "Demo root: $Demo"

New-Item -ItemType Directory -Path @(
    (Join-Path $Demo 'source'),
    (Join-Path $Demo 'staging'),
    (Join-Path $Demo 'results'),
    (Join-Path $Demo 'retrieved')
) | Out-Null

Set-Content -Path (Join-Path $Demo 'source\payload.txt') -Value 'sample payload' -Encoding utf8
Set-Content -Path (Join-Path $Demo 'source\meta.txt') -Value 'run: 42' -Encoding utf8

$Config = Join-Path $Demo 'config.yaml'
@"
backend: local
source_dir: $($Demo -replace '\\','/')/source
staging_dir: $($Demo -replace '\\','/')/staging
results_dir: $($Demo -replace '\\','/')/results
retrieve_to: $($Demo -replace '\\','/')/retrieved
"@ | Set-Content -Path $Config -Encoding utf8

$Wrapper = Join-Path $PSScriptRoot 'verified-xfer.ps1'

Write-Host '=== STAGE (dry-run) ==='
& $Wrapper stage -c $Config --dry-run
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '=== STAGE ==='
& $Wrapper stage -c $Config
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '=== Simulate test producing results ==='
Set-Content -Path (Join-Path $Demo 'results\test.log') -Value 'PASS' -Encoding utf8
Set-Content -Path (Join-Path $Demo 'results\answer.txt') -Value '42' -Encoding utf8

Write-Host '=== RETRIEVE ==='
& $Wrapper retrieve -c $Config
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host '=== Retrieved contents ==='
Get-ChildItem (Join-Path $Demo 'retrieved') | ForEach-Object { $_.Name }
Get-Content (Join-Path $Demo 'retrieved\test.log')

Write-Host "Demo complete.  Temp dir left at $Demo (remove manually)."
exit 0
