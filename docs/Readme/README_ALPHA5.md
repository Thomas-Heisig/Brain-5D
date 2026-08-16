# Brain-5D v0.4.0-alpha.5 - Operator Dashboard & Quality Gate

Diese Revision baut auf alpha.4 auf und fuegt eine lokale Operator-Konsole hinzu.
Sie ist bewusst read-only und verwendet keine neue Web-Framework-Abhaengigkeit.

## Start

```powershell
python -m src.dashboard --snapshot artifacts/brain5d_snapshot.b5d
```

Browser:

```text
http://127.0.0.1:8765
```

## Qualitaetsziel vor v0.4.0 final

```powershell
black src tests
python -m pytest -v
black --check src tests
mypy src
pylint src
python scripts/verify_dashboard.py
git diff --check
```

Die beiden strategischen Dokumente `docs/Analyse_Deepseek.md` und
`docs/Der_weg_zur_KI.md` werden nach ihrem Push in einem separaten Strategy
Review mit der bestehenden Roadmap abgeglichen.
