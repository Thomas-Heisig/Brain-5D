# Brain-5D v0.4.0-alpha.3 Windows Recovery Hotfix

This overlay fixes Windows `Errno 9: Bad file descriptor` during recovery
publication. No binary format changes are introduced.

After applying, run:

```powershell
python -m pytest tests/test_recovery.py -v
python scripts/verify_b5d.py
```
