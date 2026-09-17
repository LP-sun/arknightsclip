param(
    [string]$InputJson = 'inputs/five_operators.json',
    [string]$Catalog = 'config/cards_assets.json',
    [string]$OutputDirectory = '',
    [ValidateSet('3l2r','4l4r')][string]$Layout = '3l2r',
    [string]$Python = '',
    [switch]$PrepareOnly,
    [string]$McpConfig = "$env:USERPROFILE/.codex/config.toml"
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not $Python) { $Python = Join-Path $projectRoot '.venv-pencil/Scripts/python.exe' }
    if (-not $OutputDirectory) { $OutputDirectory = 'delivery/template_' + (Get-Date -Format 'yyyyMMdd_HHmmss') }
    & $Python scripts/template_batch.py $InputJson --catalog $Catalog --layout $Layout --out $OutputDirectory
    if ($LASTEXITCODE -ne 0) { throw 'Template job compilation failed' }
    if (-not $PrepareOnly) {
        & $Python scripts/pencil_batch.py run "$OutputDirectory/run.json" --config $McpConfig
        if ($LASTEXITCODE -ne 0) { throw 'Native export failed; inspect error and retained run' }
    }
    Write-Output "Run: $OutputDirectory/run.json"
} finally { Pop-Location }
