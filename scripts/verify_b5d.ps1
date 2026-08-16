# Brain-5D v0.4.0-alpha.1 final Storage V1 verification.

$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Label,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host "`n[$Label]" -ForegroundColor Yellow
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

Write-Host "Brain-5D v0.4.0-alpha.1 - .b5d Storage V1 Final Verification" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

Invoke-Checked "1/8 Install/update dev environment" { python -m pip install -e ".[dev]" }
Invoke-Checked "2/8 Storage robustness tests" { python -m pytest tests/test_b5d_storage.py -v }
Invoke-Checked "3/8 Full repository regression" { python -m pytest -v }
Invoke-Checked "4/8 Black" { python -m black --check src/storage/b5d.py tests/test_b5d_storage.py }
Invoke-Checked "5/8 mypy strict" { python -m mypy src/storage/b5d.py }
Invoke-Checked "6/8 Pylint" { python -m pylint src/storage/b5d.py }
Invoke-Checked "7/8 Frozen format invariants" {
    python -c "from src.storage.b5d import assert_format_invariants; assert_format_invariants(); print('B5D V1 invariants: OK')"
}

Write-Host "`n[8/8 50k mmap/storage smoke test]" -ForegroundColor Yellow
$previousLargeTest = $env:BRAIN5D_RUN_LARGE_STORAGE_TEST
try {
    $env:BRAIN5D_RUN_LARGE_STORAGE_TEST = "1"
    python -m pytest tests/test_b5d_storage.py::test_large_storage_50k_neurons -v -s
    if ($LASTEXITCODE -ne 0) {
        throw "50k storage smoke test failed with exit code $LASTEXITCODE"
    }
}
finally {
    if ($null -eq $previousLargeTest) {
        Remove-Item Env:BRAIN5D_RUN_LARGE_STORAGE_TEST -ErrorAction SilentlyContinue
    }
    else {
        $env:BRAIN5D_RUN_LARGE_STORAGE_TEST = $previousLargeTest
    }
}

Write-Host "`nAll .b5d V1 checks completed successfully." -ForegroundColor Green
Write-Host "Pylance: open the workspace with pyrightconfig.json; b5d.py is strict and contains no Any annotations." -ForegroundColor DarkGray
