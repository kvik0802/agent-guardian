# Full verification: install, test, quickstart example
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$py = "python"

Write-Host "==> Installing agent-guardian (editable)..." -ForegroundColor Cyan
& $py -m pip install -e ".[dev]" -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Running pytest..." -ForegroundColor Cyan
& $py -m pytest tests/ -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Quickstart example..." -ForegroundColor Cyan
& $py -c "from agent_guardian.demos import run_quickstart; run_quickstart()"

Write-Host "`nAll verification passed." -ForegroundColor Green
