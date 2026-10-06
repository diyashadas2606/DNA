$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $projectPython)) { throw 'Create .venv and install requirements.txt first. See README.md.' }
if (-not (Test-Path -LiteralPath 'artifacts\hcv\model.joblib')) {
    & $projectPython train.py
    if ($LASTEXITCODE -ne 0) { throw 'Training failed.' }
}
Write-Host 'Open http://127.0.0.1:5000 in your browser. Press Ctrl+C to stop.'
& $projectPython app.py

