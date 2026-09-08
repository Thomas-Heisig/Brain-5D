# Hugging Face Repository Konfiguration

Dieses Verzeichnis enthält Konfigurationsdateien für das Hugging Face Repository von MHRN.

## Dateien

- `metadata.yaml` — Hugging Face Card Metadata (Tags, Lizenzen, etc.)

## Hinweise

- **Haupt-README**: Die Datei `HF_README.md` im Projektstamm ist die Hugging Face-spezifische README.
- **Kanonische Quelle**: GitHub `main` ist die Quelle der Wahrheit; Hugging Face wird daraus gespiegelt.
- **Aktueller Stand**: Die Dashboard-README beschreibt auch die gemeinsamen deutschen Vorlesesteuerungen fuer File Viewer und Research Chat.
- **LICENSE**: MIT-Lizenz — bereits im Projektstamm vorhanden.
- **Git LFS**: `.gitattributes` im Projektstamm konfiguriert Git LFS für große Dateien.

Die GitHub-Aktion `.github/workflows/sync-huggingface.yml` veröffentlicht den aktuellen
Quellbaum und alle erreichbaren Git-LFS-Objekte. Dafür müssen `HF_USERNAME` und `HF_TOKEN`
als Actions Secrets hinterlegt sein.

## Erstellung des Hugging Face Repositories

```bash
# Hugging Face CLI installieren
pip install huggingface-hub

# Einloggen
huggingface-cli login

# Repository erstellen (einmalig)
huggingface-cli repo create MHRN --type model --organization <your-org>

# Zum lokalen HF-Zweig pushen
git remote add huggingface https://huggingface.co/<your-org>/MHRN
git push huggingface main
```
