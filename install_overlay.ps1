$ErrorActionPreference = "Stop"

Write-Host "Brain-5D v0.5.0-alpha.3 overlay"
Write-Host "This script does not overwrite integration hubs automatically."
Write-Host "New modules/assets are already placed by extracting the overlay."
Write-Host ""

if (-not (Test-Path "pyproject.toml")) {
    throw "Run this script from the Brain-5D repository root."
}

Write-Host "Checking server patch..."
git apply --check patches/server_v050a3.patch
Write-Host "Server patch can be applied with: git apply patches/server_v050a3.patch"
Write-Host ""
Write-Host "Then integrate the dashboard fragment and main-loop wiring as documented in:"
Write-Host "  OVERLAY_README.md"
Write-Host "  patches/main_v050a3_integration.txt"
