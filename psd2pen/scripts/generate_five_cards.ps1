param(
    [string]$InputJson = 'inputs/five_operators.json',
    [string]$OutputDirectory = '',
    [string]$Python = '',
    [string]$McpConfig = "$env:USERPROFILE/.codex/config.toml"
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    if (-not $Python) { $Python = Join-Path $projectRoot '.venv-pencil/Scripts/python.exe' }
    if (-not $OutputDirectory) { $OutputDirectory = 'delivery/five_slot_' + (Get-Date -Format 'yyyyMMdd_HHmmss') }
    & $Python scripts/cards_pipeline.py prepare $InputJson --layout 3l2r --out $OutputDirectory
    if ($LASTEXITCODE -ne 0) { throw 'JSON validation/compilation failed' }
    & $Python scripts/pencil_batch.py run "$OutputDirectory/run.json" --config $McpConfig
    if ($LASTEXITCODE -ne 0) { throw 'Pencil rendering/verification failed; inspect the run and retry its manifest' }
    Write-Output "Completed: $OutputDirectory/verification.json"
} finally {
    Pop-Location
}
