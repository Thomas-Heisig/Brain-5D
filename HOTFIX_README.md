# Applying v0.4.0-alpha.4

1. Extract this overlay into the Brain-5D repository.
2. Run `python scripts/prepare_alpha4.py` once. This applies the narrow legacy
   mypy fixes identified by the 104-test alpha.3 acceptance run and normalizes
   Python files with Black.
3. Run `python scripts/verify_b5d.py`.
4. Do not tag v0.4.0 final until `tests/test_restore_continue.py` also passes on
   the real core and the complete mypy/Pylint gates are green.

The overlay does not change the frozen `.b5d` V1 or journal V1 binary formats.
