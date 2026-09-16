$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python environment setup failed' }
}
$Python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
& $Python -m pip install -e '.[test]'
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $Python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Runtime verification failed' }
Write-Host 'Runtime tests PASS. Live inference and engineering validation are separate gates.' -ForegroundColor Green
