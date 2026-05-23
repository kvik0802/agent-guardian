# Full verification: install, test, all demos (no PYTHONPATH needed)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$py = "python"

Write-Host "==> Installing agent-guardian (editable)..." -ForegroundColor Cyan
& $py -m pip install -e ".[dev]" -q
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Running pytest..." -ForegroundColor Cyan
& $py -m pytest tests/ -q --tb=short
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Demo: Destroyer (must BLOCK)..." -ForegroundColor Cyan
& $py -c "from agent_guardian.demos import run_destroyer; run_destroyer()"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "==> Demo: Leaker..." -ForegroundColor Cyan
& $py -c "from agent_guardian.demos import run_leaker; run_leaker()"

Write-Host "==> Demo: Undo..." -ForegroundColor Cyan
& $py -c "from agent_guardian.demos import run_undo; run_undo()"

Write-Host "`nAll verification passed." -ForegroundColor Green
