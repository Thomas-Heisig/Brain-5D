"""Cross-platform verification runner for Brain-5D persistence releases."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Sequence

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
PYTHON: Final[str] = sys.executable


@dataclass(frozen=True, slots=True)
class VerificationStep:
    """One fail-fast verification command."""

    name: str
    command: tuple[str, ...]
    optional_executable: str | None = None


def _run(step: VerificationStep) -> None:
    """Run one step and stop the process on the first failure."""
    if step.optional_executable is not None:
        if shutil.which(step.optional_executable) is None:
            print(f"\n== {step.name} ==")
            print(f"SKIPPED: {step.optional_executable} executable not installed")
            return

    print(f"\n== {step.name} ==")
    completed = subprocess.run(step.command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(f"{step.name} failed with exit code {completed.returncode}")


def _base_steps() -> tuple[VerificationStep, ...]:
    """Return the normal release-verification steps."""
    test_files: tuple[str, ...] = (
        "tests/test_b5d_storage.py",
        "tests/test_crc.py",
        "tests/test_delta_journal.py",
        "tests/test_recovery.py",
        "tests/test_storage_runtime.py",
        "tests/test_lazy_storage_view.py",
        "tests/test_async_storage.py",
        "tests/test_checkpoint.py",
        "tests/test_compaction.py",
        "tests/test_restore_continue.py",
    )
    black_targets: tuple[str, ...] = ("src", "tests")

    return (
        VerificationStep(
            "Install dev dependencies",
            (PYTHON, "-m", "pip", "install", "-e", ".[dev]", "-q"),
        ),
        *(
            VerificationStep(
                f"Test {Path(test_file).name}",
                (PYTHON, "-m", "pytest", test_file, "-v"),
            )
            for test_file in test_files
        ),
        VerificationStep("Full regression", (PYTHON, "-m", "pytest", "-v")),
        VerificationStep(
            "Black",
            (PYTHON, "-m", "black", "--check", *black_targets),
        ),
        VerificationStep(
            "mypy strict",
            (PYTHON, "-m", "mypy", "src"),
        ),
        VerificationStep(
            "Pylint",
            (PYTHON, "-m", "pylint", "src"),
        ),
        VerificationStep(
            "Compile",
            (PYTHON, "-m", "compileall", "-q", "src/storage"),
        ),
        VerificationStep(
            "Format invariants",
            (
                PYTHON,
                "-c",
                "from src.storage import assert_format_invariants, "
                "assert_journal_format_invariants; "
                "assert_format_invariants(); "
                "assert_journal_format_invariants(); "
                "print('format invariants: OK')",
            ),
        ),
        VerificationStep(
            "Pyright strict",
            ("pyright", "src/storage"),
            optional_executable="pyright",
        ),
    )


def _large_steps() -> tuple[VerificationStep, ...]:
    """Return opt-in scale smoke tests."""
    return (
        VerificationStep(
            "50k snapshot smoke test",
            (
                PYTHON,
                "-m",
                "pytest",
                "tests/test_b5d_storage.py::test_large_storage_50k_neurons",
                "-v",
            ),
        ),
        VerificationStep(
            "100k journal smoke test",
            (
                PYTHON,
                "-m",
                "pytest",
                "tests/test_delta_journal.py::test_large_journal_100k_entries_opt_in",
                "-v",
            ),
        ),
    )


def _large_tests_enabled(environment: dict[str, str]) -> bool:
    """Return whether the opt-in large storage tests were requested."""
    return (
        environment.get("BRAIN5D_RUN_LARGE_STORAGE_TESTS") == "1"
        or environment.get("BRAIN5D_RUN_LARGE_STORAGE_TEST") == "1"
    )


def main(arguments: Sequence[str] | None = None) -> int:
    """Run all release checks and optional large persistence smoke tests."""
    del arguments
    print("Brain-5D v0.4.0-alpha.4 persistence verification")
    print("===================================================")

    for step in _base_steps():
        _run(step)

    if _large_tests_enabled(dict(os.environ)):
        for step in _large_steps():
            _run(step)
    else:
        print(
            "\nLarge storage tests skipped. Set "
            "BRAIN5D_RUN_LARGE_STORAGE_TESTS=1 to enable."
        )

    print("\nBrain-5D storage verification completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
