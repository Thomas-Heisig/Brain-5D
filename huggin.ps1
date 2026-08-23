# ------------------------------------------------------------
# 1. Token testen (ob er wirklich gültig ist)
# ------------------------------------------------------------
$token = "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # <-- HIER DEINEN ECHTEN TOKEN EINFÜGEN

$headers = @{ Authorization = "Bearer $token" }
try {
    $user = Invoke-RestMethod -Uri "https://huggingface.co/api/whoami-v2" -Headers $headers
    Write-Host "✅ Token ist GÜLTIG! Angemeldet als: $($user.name)" -ForegroundColor Green
} catch {
    Write-Host "❌ Token ist UNGÜLTIG oder ABGELAUFEN!" -ForegroundColor Red
    Write-Host "   HTTP-Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    Write-Host "   Bitte erstelle einen NEUEN Token unter: https://huggingface.co/settings/tokens" -ForegroundColor Yellow
    exit 1
}

# ------------------------------------------------------------
# 2. Prüfen, ob VS Code Insiders läuft – und ggf. schließen
# ------------------------------------------------------------
$processName = "Code - Insiders"  # für Insiders; für stable: "Code"
$running = Get-Process -Name $processName -ErrorAction SilentlyContinue
if ($running) {
    Write-Host "`n⚠️  VS Code Insiders läuft noch." -ForegroundColor Yellow
    $choice = Read-Host "Möchtest du VS Code jetzt schließen? (j/n)"
    if ($choice -ne 'j') {
        Write-Host "❌ Abgebrochen – bitte schließe VS Code manuell und starte das Skript erneut." -ForegroundColor Red
        exit 0
    }
    Write-Host "🔄 Schließe VS Code Insiders ..." -ForegroundColor Cyan
    Stop-Process -Name $processName -Force
    Start-Sleep -Seconds 2
} else {
    Write-Host "✅ VS Code Insiders ist nicht gestartet – perfekt." -ForegroundColor Green
}

# ------------------------------------------------------------
# 3. Alte Erweiterung deinstallieren (nur wenn VS Code zu ist)
# ------------------------------------------------------------
Write-Host "`n🗑️  Deinstalliere Hugging Face Erweiterung ..." -ForegroundColor Cyan
code-insiders --uninstall-extension huggingface.huggingface-vscode-chat

# ------------------------------------------------------------
# 4. Gespeicherte Token aus settings.json entfernen
# ------------------------------------------------------------
$settingsPath = "$env:APPDATA\Code - Insiders\User\settings.json"
if (Test-Path $settingsPath) {
    Write-Host "📝 Entferne 'huggingface.token' aus settings.json ..." -ForegroundColor Cyan
    $json = Get-Content $settingsPath -Raw | ConvertFrom-Json
    if ($json.PSObject.Properties.Name -contains 'huggingface.token') {
        $json.PSObject.Properties.Remove('huggingface.token')
        $json | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
        Write-Host "   ✅ Eintrag entfernt." -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Kein Eintrag in settings.json gefunden." -ForegroundColor Yellow
    }
}

# ------------------------------------------------------------
# 5. Erweiterungs-Cache / Secure Storage-Daten löschen
# ------------------------------------------------------------
$extStorage = "$env:APPDATA\Code - Insiders\User\globalStorage\huggingface.huggingface-vscode-chat"
if (Test-Path $extStorage) {
    Write-Host "🧹 Lösche Erweiterungs-Cache ..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force $extStorage
    Write-Host "   ✅ Cache gelöscht." -ForegroundColor Green
}

# Windows-Anmeldeverwaltung (Credential Manager) bereinigen
Write-Host "🔑 Lösche eventuelle Windows-Anmeldeinformationen für Hugging Face ..." -ForegroundColor Cyan
cmdkey /list | Select-String "huggingface" | ForEach-Object {
    $target = $_ -replace ".*Target: (.+)", '$1'
    if ($target) {
        cmdkey /delete $target
        Write-Host "   ✅ Gelöscht: $target" -ForegroundColor Green
    }
}

# ------------------------------------------------------------
# 6. Erweiterung NEU installieren
# ------------------------------------------------------------
Write-Host "`n📦 Installiere Hugging Face Erweiterung neu ..." -ForegroundColor Cyan
code-insiders --install-extension huggingface.huggingface-vscode-chat

# ------------------------------------------------------------
# 7. Fertig – Anleitung für den nächsten Schritt
# ------------------------------------------------------------
Write-Host "`n🎉 ALLE SCHRITTE ABGESCHLOSSEN!" -ForegroundColor Green
Write-Host "`n👉 Öffne nun VS Code Insiders und gehe wie folgt vor:" -ForegroundColor Cyan
Write-Host "   1. Öffne den Copilot Chat" -ForegroundColor White
Write-Host "   2. Wähle ein Hugging Face Modell aus (oder gehe in 'Manage Models...')" -ForegroundColor White
Write-Host "   3. Wenn nach dem Token gefragt wird, füge ihn sorgfältig ein (ohne Leerzeichen)." -ForegroundColor Yellow
Write-Host "   4. Drücke Enter – der 401-Fehler sollte verschwunden sein." -ForegroundColor Green
Read-Host "`nDrücke Enter, um das Terminal zu schließen"