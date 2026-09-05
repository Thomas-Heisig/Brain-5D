from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"patch target missing: {label}")
    return text.replace(old, new, 1)


# Register an omnibus diagnostic question. A complete suite must not masquerade as
# primary evidence for one specialist research question.
questions = Path("research/registry/questions.yaml")
text = questions.read_text(encoding="utf-8")
if "RQ-SUITE-001" not in text:
    text += """
- id: RQ-SUITE-001
  domain: Research Infrastructure
  question: Erzeugt der vollstaendige Science-Suite-Lauf unter gemeinsamer Provenienz vollstaendige und intern konsistente Diagnoseartefakte fuer alle registrierten Teilprotokolle?
  relevance: Trennt technische Omnibus-Validierung von hypothesenspezifischer wissenschaftlicher Evidenz.
  literature: []
  hypotheses:
  - H-SUITE-001-A
  evidence: []
  status: open
  answer:
    current: null
    confidence: none
    limitations: Omnibus-Diagnostik ist keine Primaerevidenz fuer die enthaltenen Fach-RQs.
  created: '2026-09-05'
  updated: '2026-09-05'
"""
    questions.write_text(text, encoding="utf-8")

hypotheses = Path("research/registry/hypotheses.yaml")
text = hypotheses.read_text(encoding="utf-8")
if "H-SUITE-001-A" not in text:
    text += """
- id: H-SUITE-001-A
  research_question: RQ-SUITE-001
  hypothesis: Alle Science-Suite-Teilprotokolle erfuellen in einem gemeinsamen Lauf ihre registrierten Ausfuehrungsvertraege und erzeugen auswertbare DATA-, Statistik- und Provenienzartefakte.
  status: untested
  evidence: []
  created: '2026-09-05'
  updated: '2026-09-05'
"""
    hypotheses.write_text(text, encoding="utf-8")

# Correct the dashboard preset.
workflow_js = Path("src/dashboard/static/experiment-workflow.js")
text = workflow_js.read_text(encoding="utf-8")
old = 'question: "RQ-SNN-001",\n        hypothesis: "H-SNN-001-A",\n        title: "Complete science suite",'
if old in text:
    text = text.replace(
        old,
        'question: "RQ-SUITE-001",\n        hypothesis: "H-SUITE-001-A",\n        title: "Complete science suite diagnostic",',
        1,
    )
workflow_js.write_text(text, encoding="utf-8")

# Execution/provenance hardening.
workflow = Path("src/dashboard/experiment_workflow.py")
text = workflow.read_text(encoding="utf-8")
if "import gzip" not in text:
    text = text.replace(
        "import hashlib\nimport json\n",
        "import gzip\nimport hashlib\nimport json\nimport marshal\nimport re\n",
        1,
    )

needle = """        runner = getattr(experiment_suite, runner_name)
        tick_aware_runners = {
"""
if "runtime_runner_digest" not in text:
    text = replace_once(
        text,
        needle,
        """        runner = getattr(experiment_suite, runner_name)
        runtime_runner_digest, source_runner_digest = _assert_loaded_callable_matches_source(
            runner, Path(experiment_suite.__file__).resolve(), runner_name
        )
        summary_runtime_digest, summary_source_digest = _assert_loaded_callable_matches_source(
            write_detailed_experiment_summary,
            Path(write_detailed_experiment_summary.__code__.co_filename).resolve(),
            "write_detailed_experiment_summary",
        )
        tick_aware_runners = {
""",
        "runtime/source guard",
    )

old = """        serialized_runs = [asdict(run) for run in runs]
        data_path.write_text(
            json.dumps(serialized_runs, indent=2, sort_keys=True, default=list) + "\\n",
            encoding="utf-8",
        )
        statistics_path = write_statistics_artifact(output_dir, serialized_runs)
"""
if "trace_paths = _externalize_large_traces" not in text:
    text = replace_once(
        text,
        old,
        """        serialized_runs = [asdict(run) for run in runs]
        # Compute statistics from the complete in-memory observations first. Large
        # per-tick traces are then moved to compressed sidecars so runs.json remains
        # reviewable without discarding raw observations.
        statistics_path = write_statistics_artifact(output_dir, serialized_runs)
        trace_paths = _externalize_large_traces(output_dir, serialized_runs)
        data_path.write_text(
            json.dumps(serialized_runs, indent=2, sort_keys=True, default=list) + "\\n",
            encoding="utf-8",
        )
""",
        "trace externalization",
    )

old = """        recorder.record_provenance_digests(
            code_digest=_sha256_file(Path(experiment_suite.__file__)),
            config_digest=config_digest,
            prompt_digest=hashlib.sha256(b"NO_PROMPT").hexdigest(),
            data_digest=_sha256_file(data_path),
        )
"""
if "data_digest=_sha256_files" not in text:
    text = replace_once(
        text,
        old,
        """        recorder.record_provenance_digests(
            code_digest=_sha256_file(Path(experiment_suite.__file__)),
            config_digest=config_digest,
            prompt_digest=hashlib.sha256(b"NO_PROMPT").hexdigest(),
            data_digest=_sha256_files([data_path, *trace_paths]),
        )
""",
        "complete data digest",
    )

old = """        manifest["execution_contract"] = {
            "resolved_runner": runner_name,
            "ticks_requested": workflow.ticks,
            "tick_validation": tick_validation,
            "question_id": workflow.question_id,
            "hypothesis_id": workflow.hypothesis_id,
            "protocol": workflow.protocol,
        }
"""
if "source_runtime_consistency" not in text:
    text = replace_once(
        text,
        old,
        """        manifest["execution_contract"] = {
            "resolved_runner": runner_name,
            "ticks_requested": workflow.ticks,
            "tick_validation": tick_validation,
            "question_id": workflow.question_id,
            "hypothesis_id": workflow.hypothesis_id,
            "protocol": workflow.protocol,
            "runtime_runner_bytecode_sha256": runtime_runner_digest,
            "source_runner_bytecode_sha256": source_runner_digest,
            "runtime_summary_bytecode_sha256": summary_runtime_digest,
            "source_summary_bytecode_sha256": summary_source_digest,
            "source_runtime_consistency": "MATCH",
        }
        if trace_paths:
            artifacts["raw_trace_index"] = "DATA/traces/index.json"
""",
        "manifest source/runtime provenance",
    )

marker = "\n\ndef _load_yaml(path: Path) -> dict[str, Any]:\n"
if "def _assert_loaded_callable_matches_source(" not in text:
    helpers = r'''

def _find_named_code(code: object, name: str) -> object | None:
    if not hasattr(code, "co_consts"):
        return None
    if getattr(code, "co_name", None) == name:
        return code
    for value in code.co_consts:
        found = _find_named_code(value, name)
        if found is not None:
            return found
    return None


def _code_digest(code: object) -> str:
    return hashlib.sha256(marshal.dumps(code)).hexdigest()


def _assert_loaded_callable_matches_source(
    function: Callable[..., object], source_path: Path, function_name: str
) -> tuple[str, str]:
    """Block scientific runs when a long-lived process still holds stale code."""
    runtime_digest = _code_digest(function.__code__)
    compiled = compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")
    source_code = _find_named_code(compiled, function_name)
    if source_code is None:
        raise WorkflowValidationError(
            f"Cannot verify runtime/source consistency for {function_name}."
        )
    source_digest = _code_digest(source_code)
    if runtime_digest != source_digest:
        raise WorkflowValidationError(
            f"Running process contains stale code for {function_name}. Restart the Brain-5D "
            "dashboard/runtime before creating a scientific experiment."
        )
    return runtime_digest, source_digest


def _safe_trace_name(condition: object, seed: object) -> str:
    label = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(condition)).strip("-") or "trace"
    return f"{label}-seed-{seed}.jsonl.gz"


def _externalize_large_traces(
    output_dir: Path, serialized_runs: list[dict[str, Any]], threshold: int = 10_000
) -> list[Path]:
    """Keep complete large traces compressed and references inside compact DATA."""
    trace_dir = output_dir / "DATA" / "traces"
    trace_entries: list[dict[str, object]] = []
    written: list[Path] = []
    for run in serialized_runs:
        metrics = run.get("metrics")
        if not isinstance(metrics, dict):
            continue
        comparisons = metrics.get("comparisons")
        if not isinstance(comparisons, list) or len(comparisons) <= threshold:
            continue
        trace_dir.mkdir(parents=True, exist_ok=True)
        path = trace_dir / _safe_trace_name(run.get("condition"), run.get("seed"))
        with gzip.open(path, "wt", encoding="utf-8", newline="\n", compresslevel=9) as handle:
            for item in comparisons:
                handle.write(
                    json.dumps(
                        item,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )
                handle.write("\n")
        digest = _sha256_file(path)
        count = len(comparisons)
        metrics["comparisons_artifact"] = {
            "path": path.relative_to(output_dir).as_posix(),
            "format": "jsonl.gz",
            "count": count,
            "sha256": digest,
        }
        metrics["comparisons_preview"] = comparisons[:8] + comparisons[-8:]
        del metrics["comparisons"]
        trace_entries.append(
            {
                "condition": run.get("condition"),
                "seed": run.get("seed"),
                "path": path.relative_to(output_dir).as_posix(),
                "count": count,
                "sha256": digest,
                "size_bytes": path.stat().st_size,
            }
        )
        written.append(path)
    if trace_entries:
        index_path = trace_dir / "index.json"
        index_path.write_text(
            json.dumps(
                {"schema_version": "1.0", "traces": trace_entries},
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        written.append(index_path)
    return written


def _sha256_files(paths: Sequence[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda item: item.as_posix()):
        digest.update(path.relative_to(path.parent.parent.parent).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
'''
    text = replace_once(text, marker, helpers + marker, "helper insertion")
workflow.write_text(text, encoding="utf-8")

# Statistics and summary hardening.
summary = Path("src/research/experiment_summary.py")
text = summary.read_text(encoding="utf-8")
if '"p_success_after"' not in text.split("numeric_metric_names", 1)[1].split(")", 1)[0]:
    text = replace_once(
        text,
        '        "reward_weight_updates",\n    )',
        '        "reward_weight_updates",\n        "p_success_before",\n        "p_success_after",\n        "train_trial_count",\n        "validation_trial_count",\n        "holdout_trial_count",\n    )',
        "learning statistics",
    )

old = """        conditions[condition] = {
            "run_count": len(condition_runs),
"""
if '"functional_activation"' not in text:
    text = replace_once(
        text,
        old,
        """        nested_paths = {
            "functional_activation": ("functional_state", "activation"),
            "functional_safety": ("functional_state", "safety"),
            "functional_valence": ("functional_state", "valence"),
            "functional_uncertainty": ("functional_state", "uncertainty"),
            "regulatory_continuity_risk": ("regulatory_state", "values", "continuity_risk"),
            "regulatory_energy_reserve": ("regulatory_state", "values", "energy_reserve"),
            "regulatory_resource_pressure": ("regulatory_state", "values", "resource_pressure"),
            "regulatory_sensory_integrity": ("regulatory_state", "values", "sensory_integrity"),
            "regulatory_thermal_margin": ("regulatory_state", "values", "thermal_margin"),
        }
        for name, path in nested_paths.items():
            values: list[float] = []
            for run in condition_runs:
                current: object = run.get("metrics") or {}
                for part in path:
                    current = current.get(part) if isinstance(current, dict) else None
                value = _number(current)
                if value is not None:
                    values.append(value)
            if values:
                metric_stats[name] = _stats(values)
        conditions[condition] = {
            "run_count": len(condition_runs),
""",
        "regulation statistics",
    )

old = """        temporal[horizon] = {
            "discrepancy": _stats(horizon_values[horizon]),
            "reference_comparisons": horizon_reference_counts[horizon],
        }
"""
if '"nonzero_fraction"' not in text:
    text = replace_once(
        text,
        old,
        """        horizon_all = horizon_values[horizon]
        nonzero = [value for value in horizon_all if value != 0.0]
        temporal[horizon] = {
            "discrepancy": _stats(horizon_all),
            "reference_comparisons": horizon_reference_counts[horizon],
            "nonzero_comparisons": len(nonzero),
            "nonzero_fraction": (len(nonzero) / len(horizon_all)) if horizon_all else 0.0,
            "nonzero_discrepancy": _stats(nonzero),
        }
""",
        "temporal sparsity statistics",
    )

old = """    statistics = build_descriptive_statistics(runs)
    statistics_path = write_statistics_artifact(experiment_dir, runs)
"""
if "stored_statistics = _read_json" not in text:
    text = replace_once(
        text,
        old,
        """    statistics_path = experiment_dir / "analysis" / "statistics.json"
    stored_statistics = _read_json(statistics_path, None)
    if (
        isinstance(stored_statistics, dict)
        and stored_statistics.get("generated_by") == "deterministic_statistics_engine"
    ):
        statistics = stored_statistics
    else:
        statistics = build_descriptive_statistics(runs)
        statistics_path = write_statistics_artifact(experiment_dir, runs)
""",
        "canonical stored statistics",
    )

marker = """    if question_id.startswith("RQ-5D-"):
        return classify(
            {"1d", "2d", "3d", "5d", "random_graph"}.issubset(plain),
            "5D erwartet die registrierten Dimensions-/Topologiebedingungen.",
        )
    return (
"""
if 'question_id == "RQ-SUITE-001"' not in text:
    text = replace_once(
        text,
        marker,
        """    if question_id.startswith("RQ-5D-"):
        return classify(
            {"1d", "2d", "3d", "5d", "random_graph"}.issubset(plain),
            "5D erwartet die registrierten Dimensions-/Topologiebedingungen.",
        )
    if question_id == "RQ-SUITE-001":
        required_groups = {"ping", "temporal", "stdp", "learning", "time", "5d", "regulation"}
        present_groups = {
            item.split(":", 1)[0] for item in conditions if ":" in item
        }
        found = required_groups.issubset(present_groups) and protocol == "science_all_v1"
        return (
            "DIRECT_MATCH" if found else "MISMATCH",
            "SUITE erwartet science_all_v1 und PING, TEMP, STDP, Learning, TIME, 5D sowie Regulation unter gemeinsamer Provenienz.",
        )
    if question_id == "RQ-SNN-001":
        return (
            "MISMATCH",
            "RQ-SNN-001 fordert langfristig stabile Spike-Dynamik unter fortlaufender Aktivitaet. Ein einzelner Impuls bzw. science_all_v1 mit langer stiller Nachlaufphase ist dafuer keine ausreichende Primaerpruefung.",
        )
    return (
""",
        "suite and long-term semantics",
    )

old = """    semantic_status, semantic_note = _semantic_status(question_id, protocol, conditions)

    requested_ticks = (
"""
if "evidence_readiness =" not in text:
    text = replace_once(
        text,
        old,
        """    semantic_status, semantic_note = _semantic_status(question_id, protocol, conditions)
    git_info = manifest.get("git", {}) if isinstance(manifest, dict) else {}
    git_dirty = bool(git_info.get("dirty")) if isinstance(git_info, dict) else True
    if semantic_status == "MISMATCH":
        evidence_readiness = "BLOCKED_SEMANTIC_MISMATCH"
    elif semantic_status == "NOT_AUTOMATICALLY_CLASSIFIED":
        evidence_readiness = "BLOCKED_UNCLASSIFIED_SEMANTICS"
    elif git_dirty:
        evidence_readiness = "BLOCKED_DIRTY_SOURCE_TREE"
    elif question_id == "RQ-SUITE-001":
        evidence_readiness = "DIAGNOSTIC_ONLY"
    else:
        evidence_readiness = "HUMAN_REVIEW_REQUIRED"

    requested_ticks = (
""",
        "evidence readiness",
    )

old = '        f"- RQ/Condition-Pruefung: `{semantic_status}`",\n        f"- Begründung: {semantic_note}",\n'
if "Evidence Readiness" not in text:
    text = replace_once(
        text,
        old,
        '        f"- RQ/Condition-Pruefung: `{semantic_status}`",\n        f"- Evidence Readiness: `{evidence_readiness}`",\n        f"- Begründung: {semantic_note}",\n',
        "evidence readiness output",
    )

old = """            lines.append(
                f"- `{horizon}`: Referenzvergleiche={payload.get('reference_comparisons', 0) if isinstance(payload, dict) else 0}; discrepancy mean={_fmt(discrepancy.get('mean') if isinstance(discrepancy, dict) else None)}, max={_fmt(discrepancy.get('max') if isinstance(discrepancy, dict) else None)}."
            )
"""
if "mean(nonzero)" not in text:
    text = replace_once(
        text,
        old,
        """            nonzero = (
                payload.get("nonzero_discrepancy", {})
                if isinstance(payload, dict)
                else {}
            )
            lines.append(
                f"- `{horizon}`: Referenzvergleiche={payload.get('reference_comparisons', 0) if isinstance(payload, dict) else 0}; discrepancy mean={_fmt(discrepancy.get('mean') if isinstance(discrepancy, dict) else None)}, max={_fmt(discrepancy.get('max') if isinstance(discrepancy, dict) else None)}; nonzero={payload.get('nonzero_comparisons', 0) if isinstance(payload, dict) else 0} ({_fmt(payload.get('nonzero_fraction') if isinstance(payload, dict) else None)}); mean(nonzero)={_fmt(nonzero.get('mean') if isinstance(nonzero, dict) else None)}."
            )
""",
        "temporal summary",
    )

summary.write_text(text, encoding="utf-8")

# Regression tests.
tests = Path("tests/test_scientific_execution_contract.py")
text = tests.read_text(encoding="utf-8")
if "test_suite_semantics_require_all_registered_groups" not in text:
    text += """


def test_suite_semantics_require_all_registered_groups() -> None:
    from src.research.experiment_summary import _semantic_status

    conditions = {
        "ping:recurrence_off",
        "temporal:fast_medium_slow",
        "stdp:productive_reward_stdp",
        "learning:learning_on",
        "time:1000",
        "5d:5d",
        "regulation:nominal",
    }
    status, _ = _semantic_status("RQ-SUITE-001", "science_all_v1", conditions)
    assert status == "DIRECT_MATCH"
    conditions.remove("regulation:nominal")
    status, _ = _semantic_status("RQ-SUITE-001", "science_all_v1", conditions)
    assert status == "MISMATCH"


def test_long_term_stability_is_not_claimed_from_ping_omnibus() -> None:
    from src.research.experiment_summary import _semantic_status

    status, note = _semantic_status(
        "RQ-SNN-001",
        "science_all_v1",
        {"ping:recurrence_off", "ping:recurrence_on"},
    )
    assert status == "MISMATCH"
    assert "langfristig" in note
"""
    tests.write_text(text, encoding="utf-8")
