import sys
sys.path.insert(0, ".")
with open("tests/test_restore_determinism_abc.py", "a", encoding="utf-8") as f:
    f.write('\n# Appended content\n')
print("done")
