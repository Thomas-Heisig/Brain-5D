# Hugging Face Repository Konfiguration

Dieses Verzeichnis enthält Konfigurationsdateien für das Hugging Face Repository von Brain-5D.

## Dateien

- `metadata.yaml` — Hugging Face Card Metadata (Tags, Lizenzen, etc.)

## Hinweise

- **Haupt-README**: Die Datei `HF_README.md` im Projektstamm ist die Hugging Face-spezifische README.
- **LICENSE**: MIT-Lizenz — bereits im Projektstamm vorhanden.
- **Git LFS**: `.gitattributes` im Projektstamm konfiguriert Git LFS für große Dateien.

## Erstellung des Hugging Face Repositories

```bash
# Hugging Face CLI installieren
pip install huggingface-hub

# Einloggen
huggingface-cli login

# Repository erstellen (einmalig)
huggingface-cli repo create Brain-5D --type model --organization <your-org>

# Zum lokalen HF-Zweig pushen
git remote add huggingface https://huggingface.co/<your-org>/Brain-5D
git push huggingface main
```
