param([int]$Port = 8765)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath 'build/rvc_cli.exe')) {
        & (Join-Path $PSScriptRoot 'build.ps1')
    }
    python simulator/server.py --port $Port
} finally { Pop-Location }
