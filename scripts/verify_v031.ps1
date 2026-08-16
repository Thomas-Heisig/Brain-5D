$ErrorActionPreference = "Stop"

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command
    )

    Write-Host "`n==> $Description"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Description failed with exit code $LASTEXITCODE"
    }
}

Invoke-Checked "Full pytest regression" { python -m pytest -v }
Invoke-Checked "Golden Chain regression" {
    python -m pytest tests/test_golden_chain.py -v
}
Invoke-Checked "End-to-end learning experiment" {
    python -m src.experiments.learning_lab --config configs/learning_experiment.yaml
}
Invoke-Checked "Black formatting check" {
    black --check src/learning src/experiments src/visualization/heatmap.py tests/test_learning_experiment.py tests/test_network_hooks.py
}
Invoke-Checked "Strict mypy surface" {
    mypy src/learning src/experiments src/visualization/heatmap.py
}
Invoke-Checked "Pylint surface" {
    pylint src/learning src/experiments src/visualization/heatmap.py
}
Invoke-Checked "PoC benchmark" { python -m src.main --benchmark }

Write-Host "`nBrain-5D v0.3.1 verification completed successfully."
