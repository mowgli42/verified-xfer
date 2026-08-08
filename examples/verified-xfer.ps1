#requires -Version 5.1
<#
.SYNOPSIS
  Windows PowerShell wrapper for verified-xfer (stage / retrieve).

.EXAMPLE
  .\verified-xfer.ps1 stage --dry-run
  .\verified-xfer.ps1 retrieve -c D:\lab\config.yaml
#>
$ErrorActionPreference = 'Stop'

function Resolve-PythonInvocation {
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        & $pyLauncher.Source -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Exe = $pyLauncher.Source; Prefix = @('-3') }
        }
    }
    foreach ($name in @('python', 'python3')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        & $cmd.Source -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>$null
        if ($LASTEXITCODE -eq 0) {
            return @{ Exe = $cmd.Source; Prefix = @() }
        }
    }
    throw "Python 3.10+ not found. Install Python and ensure 'py' or 'python' is on PATH."
}

$py = Resolve-PythonInvocation
$env:PYTHONUNBUFFERED = '1'
& $py.Exe @($py.Prefix + @('-m', 'verified_xfer') + $args)
exit $LASTEXITCODE
