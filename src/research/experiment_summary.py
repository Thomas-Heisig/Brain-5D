"""Deterministic, data-first experiment summaries for Brain-5D research runs."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median, pstdev
from typing import Any


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def _number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def _stats(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "mean": fmean(values),
        "median": median(values),
        "std": pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def build_descriptive_statistics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build deterministic descriptive statistics without model participation."""
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for run in runs:
        by_condition[str(run.get("condition", "unknown"))].append(run)

    numeric_metric_names = (
        "ticks_executed",
        "total_spikes",
        "activated_neurons",
        "delivered_synaptic_events",
        "synaptic_activity_ticks",
        "recurrent_events",
        "propagation_depth",
        "first_response_latency",
        "last_response_latency",
        "return_latency",
        "ticks_per_second",
        "duration_seconds",
        "mean_weight_delta",
        "initial_mean_weight",
        "final_mean_weight",
        "rewards_received",
        "reward_weight_updates",
    )
    conditions: dict[str, Any] = {}
    for condition, condition_runs in sorted(by_condition.items()):
        metric_stats: dict[str, Any] = {}
        for name in numeric_metric_names:
            values = [
                value
                for run in condition_runs
                for value in [_number((run.get("metrics") or {}).get(name))]
                if value is not None
            ]
            if values:
                metric_stats[name] = _stats(values)
        conditions[condition] = {
            "run_count": len(condition_runs),
            "seeds": sorted(
                {
                    int(run["seed"])
                    for run in condition_runs
                    if isinstance(run.get("seed"), int)
                }
            ),
            "metrics": metric_stats,
        }

    temporal: dict[str, Any] = {}
    horizon_values: dict[str, list[float]] = defaultdict(list)
    horizon_reference_counts: dict[str, int] = defaultdict(int)
    for run in runs:
        comparisons = (run.get("metrics") or {}).get("comparisons")
        if not isinstance(comparisons, list):
            continue
        for comparison in comparisons:
            if not isinstance(comparison, dict):
                continue
            horizon = str(comparison.get("horizon", "unknown"))
            discrepancy = _number(comparison.get("discrepancy"))
            if discrepancy is not None:
                horizon_values[horizon].append(discrepancy)
            if comparison.get("reference_tick") is not None:
                horizon_reference_counts[horizon] += 1
    for horizon in sorted(set(horizon_values) | set(horizon_reference_counts)):
        temporal[horizon] = {
            "discrepancy": _stats(horizon_values[horizon]),
            "reference_comparisons": horizon_reference_counts[horizon],
        }

    isi_by_condition: dict[str, Any] = {}
    for condition, condition_runs in sorted(by_condition.items()):
        intervals: list[float] = []
        for run in condition_runs:
            sequence = (run.get("metrics") or {}).get("spike_sequence")
            if not isinstance(sequence, list):
                continue
            ticks = [
                int(item["tick"])
                for item in sequence
                if isinstance(item, dict) and isinstance(item.get("tick"), int)
            ]
            intervals.extend(float(b - a) for a, b in zip(ticks, ticks[1:]))
        if intervals:
            isi_by_condition[condition] = _stats(intervals)

    result: dict[str, Any] = {
        "generated_by": "deterministic_statistics_engine",
        "schema_version": "2.0",
        "run_count": len(runs),
        "conditions": conditions,
        "formulas": {
            "mean": "mean(x) = (1/n) * sum_i x_i",
            "population_std": "sigma = sqrt((1/n) * sum_i (x_i - mean(x))^2)",
            "difference": "Delta_x = mean(x_B) - mean(x_A)",
            "ratio": "R_x = mean(x_B) / mean(x_A), defined only when mean(x_A) != 0",
            "inter_spike_interval": "ISI_i = t_(i+1) - t_i",
        },
    }
    if temporal:
        result["temporal_horizons"] = temporal
    if isi_by_condition:
        result["inter_spike_intervals"] = isi_by_condition

    condition_names = sorted(conditions)
    if len(condition_names) == 2:
        a, b = condition_names
        effects: dict[str, Any] = {}
        common = set(conditions[a]["metrics"]) & set(conditions[b]["metrics"])
        for metric in sorted(common):
            av = conditions[a]["metrics"][metric].get("mean")
            bv = conditions[b]["metrics"][metric].get("mean")
            if isinstance(av, (int, float)) and isinstance(bv, (int, float)):
                effects[metric] = {
                    "reference_condition": a,
                    "comparison_condition": b,
                    "absolute_difference": float(bv) - float(av),
                    "ratio": None if float(av) == 0.0 else float(bv) / float(av),
                }
        result["two_condition_effects"] = effects
    return result


def write_statistics_artifact(experiment_dir: Path, runs: list[dict[str, Any]]) -> Path:
    """Persist deterministic statistics so AIRR and summary share one numeric source."""
    path = experiment_dir / "analysis" / "statistics.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            build_descriptive_statistics(runs),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _semantic_status(question_id: str, conditions: set[str]) -> tuple[str, str]:
    plain = {item.split(":", 1)[-1] for item in conditions}
    if question_id.startswith("RQ-PING-"):
        ok = {"recurrence_off", "recurrence_on"}.issubset(plain)
        return (
            "MATCH" if ok else "MISMATCH",
            "PING erwartet recurrence_off und recurrence_on.",
        )
    if question_id.startswith("RQ-TEMP-"):
        ok = "fast_medium_slow" in plain
        return (
            "MATCH" if ok else "MISMATCH",
            "TEMP erwartet fast_medium_slow mit FAST/MEDIUM/SLOW-Horizonten.",
        )
    if question_id.startswith("RQ-TIME-"):
        ok = bool(plain) and all(item.isdigit() for item in plain)
        return (
            "MATCH" if ok else "MISMATCH",
            "TIME erwartet numerische Tick-Leiter-Bedingungen.",
        )
    if question_id.startswith("RQ-5D-"):
        expected = {"1d", "2d", "3d", "5d", "random_graph"}
        ok = expected.issubset(plain)
        return (
            "MATCH" if ok else "MISMATCH",
            "5D erwartet die registrierten Dimensions-/Topologiebedingungen.",
        )
    return (
        "NOT_AUTOMATICALLY_CLASSIFIED",
        "Keine automatische semantische Regel fuer diese RQ-Familie registriert.",
    )


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.6g}"
    if value is None:
        return "—"
    return str(value)


def write_detailed_experiment_summary(
    research_root: Path, experiment_id: str, ai_report: dict[str, object]
) -> str:
    """Write a comprehensive data-first summary beside one experiment."""
    experiment_dir = research_root / "experiments" / experiment_id
    manifest = _read_json(experiment_dir / "manifest.json", {})
    workflow = _read_json(experiment_dir / "workflow.json", {})
    raw_runs = _read_json(experiment_dir / "DATA" / "runs.json", [])
    runs = (
        [item for item in raw_runs if isinstance(item, dict)]
        if isinstance(raw_runs, list)
        else []
    )
    statistics = build_descriptive_statistics(runs)
    statistics_path = write_statistics_artifact(experiment_dir, runs)

    simulation = manifest.get("simulation", {}) if isinstance(manifest, dict) else {}
    results = manifest.get("results", {}) if isinstance(manifest, dict) else {}
    question_ids = (
        manifest.get("research_questions", []) if isinstance(manifest, dict) else []
    )
    hypothesis_ids = (
        manifest.get("hypotheses", []) if isinstance(manifest, dict) else []
    )
    question_id = (
        str(question_ids[0])
        if isinstance(question_ids, list) and question_ids
        else "NOT_AVAILABLE"
    )
    conditions = {str(run.get("condition", "unknown")) for run in runs}
    semantic_status, semantic_note = _semantic_status(question_id, conditions)

    requested_ticks = (
        simulation.get("ticks", workflow.get("ticks", "NOT_AVAILABLE"))
        if isinstance(simulation, dict)
        else workflow.get("ticks", "NOT_AVAILABLE")
    )
    actual_ticks = [
        int(value)
        for run in runs
        for value in [(run.get("metrics") or {}).get("ticks_executed")]
        if isinstance(value, int)
    ]
    tick_contract = "NOT_APPLICABLE"
    if isinstance(requested_ticks, int) and actual_ticks:
        tick_contract = (
            "SATISFIED" if min(actual_ticks) >= requested_ticks else "VIOLATED"
        )

    lines = [
        f"# {experiment_id}: Wissenschaftliche Zusammenfassung",
        "",
        "Diese Zusammenfassung wird deterministisch aus Manifest, Workflow, DATA und — sofern vorhanden — dem AIRR aufgebaut. Zahlen und Formeln stammen aus den gespeicherten Laufdaten beziehungsweise dem deterministischen Statistics Engine; KI-Text bleibt davon getrennt.",
        "",
        "## 1. Identifikation und Status",
        "",
        f"- Experimentstatus: `{manifest.get('experiment_status', 'unknown')}`",
        f"- Forschungsfrage: `{question_id}`",
        f"- Hypothese: `{hypothesis_ids[0] if isinstance(hypothesis_ids, list) and hypothesis_ids else 'NOT_AVAILABLE'}`",
        f"- Protokoll: `{simulation.get('protocol', workflow.get('protocol', 'NOT_AVAILABLE')) if isinstance(simulation, dict) else workflow.get('protocol', 'NOT_AVAILABLE')}`",
        f"- Durchlaeufe: `{results.get('run_count', len(runs)) if isinstance(results, dict) else len(runs)}`",
        f"- Seeds: `{simulation.get('seeds', workflow.get('seeds', [])) if isinstance(simulation, dict) else workflow.get('seeds', [])}`",
        f"- Angeforderte Ticks: `{requested_ticks}`",
        f"- Tatsächlich ausgeführte Ticks je Lauf: `{min(actual_ticks) if actual_ticks else 'nicht direkt messbar'} .. {max(actual_ticks) if actual_ticks else 'nicht direkt messbar'}`",
        f"- Tick-Vertrag: `{tick_contract}`",
        f"- Laufmodus: `{manifest.get('research_run_mode', 'unknown')}`",
        f"- Netzwerkmodus: `{manifest.get('network_mode', 'unknown')}`",
        "",
        "## 2. Semantische Konsistenz",
        "",
        f"- RQ/Condition-Pruefung: `{semantic_status}`",
        f"- Begründung: {semantic_note}",
        f"- Beobachtete Conditions: `{', '.join(sorted(conditions)) or 'keine'}`",
        "",
        "Ein semantischer Mismatch blockiert die Nutzung des Laufs als Evidenz fuer die registrierte Forschungsfrage, auch wenn die technische Ausfuehrung fehlerfrei war.",
        "",
        "## 3. Ausfuehrungsparameter",
        "",
        f"- Titel: {workflow.get('title', 'NOT_AVAILABLE')}",
        f"- Bedingungen: {workflow.get('conditions', 'NOT_AVAILABLE')}",
        f"- Notizen: {workflow.get('notes') or 'Keine.'}",
        f"- Konfiguration: `{(manifest.get('config') or {}).get('path', 'NOT_AVAILABLE') if isinstance(manifest.get('config'), dict) else 'NOT_AVAILABLE'}`",
        f"- Config SHA-256: `{(manifest.get('config') or {}).get('sha256', 'NOT_AVAILABLE') if isinstance(manifest.get('config'), dict) else 'NOT_AVAILABLE'}`",
        f"- Git Commit: `{(manifest.get('git') or {}).get('commit', 'NOT_AVAILABLE') if isinstance(manifest.get('git'), dict) else 'NOT_AVAILABLE'}`",
        f"- Git dirty: `{(manifest.get('git') or {}).get('dirty', 'NOT_AVAILABLE') if isinstance(manifest.get('git'), dict) else 'NOT_AVAILABLE'}`",
        f"- Runtime: `{(manifest.get('runtime') or {}).get('duration_seconds', 'NOT_AVAILABLE') if isinstance(manifest.get('runtime'), dict) else 'NOT_AVAILABLE'}` s",
        "",
        "## 4. Deterministische Formeln",
        "",
        "Die im Bericht verwendeten deskriptiven Groessen sind:",
        "",
        "- Mittelwert: $\\bar{x}=\\frac{1}{n}\\sum_{i=1}^{n}x_i$",
        "- Populationsstandardabweichung: $\\sigma=\\sqrt{\\frac{1}{n}\\sum_{i=1}^{n}(x_i-\\bar{x})^2}$",
        "- Absolute Differenz: $\\Delta_x=\\bar{x}_B-\\bar{x}_A$",
        "- Verhältnis: $R_x=\\bar{x}_B/\\bar{x}_A$ fuer $\\bar{x}_A\\neq0$",
        "- Inter-Spike-Intervall: $ISI_i=t_{i+1}-t_i$",
        "",
        "Diese Formeln sind deskriptiv. Ohne registrierten Inferenztest, unabhaengige Stichprobenannahme und passende Versuchsplanung werden daraus keine Signifikanz- oder Kausalbehauptungen abgeleitet.",
        "",
        "## 5. Ergebnisse nach Bedingung",
        "",
        "| Condition | n | Seeds | Ticks mean | Spikes mean | Syn. events mean | Aktivierte Neuronen mean | Recurrent events mean | Propagation depth mean |",
        "| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, payload in statistics.get("conditions", {}).items():
        metrics = payload.get("metrics", {})

        def mean_of(name: str) -> object:
            item = metrics.get(name, {})
            return item.get("mean") if isinstance(item, dict) else None

        lines.append(
            "| "
            + " | ".join(
                [
                    condition,
                    str(payload.get("run_count", 0)),
                    ",".join(map(str, payload.get("seeds", []))),
                    _fmt(mean_of("ticks_executed")),
                    _fmt(mean_of("total_spikes")),
                    _fmt(mean_of("delivered_synaptic_events")),
                    _fmt(mean_of("activated_neurons")),
                    _fmt(mean_of("recurrent_events")),
                    _fmt(mean_of("propagation_depth")),
                ]
            )
            + " |"
        )

    effects = statistics.get("two_condition_effects", {})
    if isinstance(effects, dict) and effects:
        lines.extend(["", "### 5.1 Deskriptive Zwei-Bedingungs-Effekte", ""])
        for metric, effect in effects.items():
            if not isinstance(effect, dict):
                continue
            lines.append(
                f"- `{metric}`: $\\Delta={_fmt(effect.get('absolute_difference'))}$; $R={_fmt(effect.get('ratio'))}$; Referenz `{effect.get('reference_condition')}`, Vergleich `{effect.get('comparison_condition')}`."
            )

    isi = statistics.get("inter_spike_intervals", {})
    if isinstance(isi, dict) and isi:
        lines.extend(["", "### 5.2 Inter-Spike-Intervalle", ""])
        for condition, stats in isi.items():
            if isinstance(stats, dict):
                lines.append(
                    f"- `{condition}`: n={stats.get('n')}, mean={_fmt(stats.get('mean'))}, median={_fmt(stats.get('median'))}, min={_fmt(stats.get('min'))}, max={_fmt(stats.get('max'))} Ticks."
                )

    temporal = statistics.get("temporal_horizons", {})
    if isinstance(temporal, dict) and temporal:
        lines.extend(["", "### 5.3 Temporal-State-Horizonte", ""])
        for horizon, payload in temporal.items():
            discrepancy = (
                payload.get("discrepancy", {}) if isinstance(payload, dict) else {}
            )
            lines.append(
                f"- `{horizon}`: Referenzvergleiche={payload.get('reference_comparisons', 0) if isinstance(payload, dict) else 0}; discrepancy mean={_fmt(discrepancy.get('mean') if isinstance(discrepancy, dict) else None)}, max={_fmt(discrepancy.get('max') if isinstance(discrepancy, dict) else None)}."
            )

    lines.extend(
        [
            "",
            "## 6. Einzelne Läufe",
            "",
            "| Seed | Condition | Ticks | Spikes | Syn. events | Aktivierte Neuronen | Recurrent events | Depth | Runtime error |",
            "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    for run in runs:
        metrics = run.get("metrics") if isinstance(run.get("metrics"), dict) else {}
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(run.get("seed")),
                    _fmt(run.get("condition")),
                    _fmt(metrics.get("ticks_executed", metrics.get("ticks"))),
                    _fmt(metrics.get("total_spikes")),
                    _fmt(metrics.get("delivered_synaptic_events")),
                    _fmt(metrics.get("activated_neurons")),
                    _fmt(metrics.get("recurrent_events")),
                    _fmt(metrics.get("propagation_depth")),
                    _fmt(run.get("runtime_error")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## 7. Reproduzierbarkeit und Provenienz",
            "",
            "Identische Ausgaben ueber mehrere Seeds dokumentieren reproduzierbare Modelltrajektorien unter diesen Bedingungen. Sie sind nicht automatisch statistisch unabhaengige Replikate. State-Digests sind Integritaets-/Identitaetsmarker und keine metrischen Zustandsabstaende.",
            "",
            f"Deterministische Statistikdatei: [`{statistics_path.relative_to(experiment_dir).as_posix()}`]({statistics_path.relative_to(experiment_dir).as_posix()})",
            "",
            "## 8. AI Research Report",
            "",
            f"- AIRR Status: `{ai_report.get('status', 'unknown')}`",
            "- Wissenschaftliche Evidenz durch KI: `false`",
            "- Human Review: `PENDING`",
        ]
    )

    if ai_report.get("status") == "generated" and ai_report.get("report_id"):
        report_id = str(ai_report["report_id"])
        report = _read_json(experiment_dir / "reports" / f"{report_id}.json", {})
        content = report.get("content", {}) if isinstance(report, dict) else {}
        lines.extend(
            [
                f"- AIRR Markdown: [`reports/{report_id}.md`](reports/{report_id}.md)",
                f"- AIRR JSON: [`reports/{report_id}.json`](reports/{report_id}.json)",
                "",
                "### 8.1 KI-Einschaetzung",
                "",
                (
                    str(
                        content.get(
                            "executive_summary",
                            content.get("conclusion", "Keine Einschätzung vorhanden."),
                        )
                    )
                    if isinstance(content, dict)
                    else "Keine Einschätzung vorhanden."
                ),
                "",
                f"KI-Konfidenz: `{content.get('ai_confidence', 0.0) if isinstance(content, dict) else 0.0}` — dies ist keine statistische Konfidenz.",
            ]
        )
        for heading, key in (
            ("Methodische Kritik", "methodological_critique"),
            ("Alternative Erklaerungen", "alternative_explanations"),
            ("Fehlende Nachweise", "missing_evidence"),
            ("Empfohlene Folgeexperimente", "recommended_follow_up"),
        ):
            values = content.get(key, []) if isinstance(content, dict) else []
            lines.extend(
                [
                    "",
                    (
                        f"### 8.2 {heading}"
                        if heading == "Methodische Kritik"
                        else f"### {heading}"
                    ),
                    "",
                ]
            )
            if isinstance(values, list) and values:
                lines.extend(f"- {value}" for value in values)
            else:
                lines.append("- Keine expliziten Angaben.")
    elif ai_report.get("status") == "failed":
        lines.extend(
            [
                "",
                f"AIRR-Fehler: `{ai_report.get('message', ai_report.get('reason', 'unknown'))}`. Die deterministische Datenauswertung oben bleibt davon unberuehrt.",
            ]
        )

    lines.extend(["", "## 9. Artefakte", ""])
    for path in sorted(experiment_dir.rglob("*")):
        if path.is_file() and path.name != "summary.md":
            relative = path.relative_to(experiment_dir).as_posix()
            lines.append(f"- [{relative}]({relative})")

    lines.extend(
        [
            "",
            "## 10. Wissenschaftliche Grenze und Schlussfolgerung",
            "",
            "Die technischen Laufdaten duerfen deskriptiv ausgewertet werden. Eine Hypothese gilt dadurch nicht automatisch als bestaetigt oder widerlegt. Kausale Aussagen sind nur fuer explizit kontrollierte Interventionen und nur innerhalb des simulierten Systems zulaessig; biologische Generalisierung erfordert zusaetzliche Evidenz. Die KI-Auswertung ist post-hoc und besitzt keine Evidenzfreigabe.",
            "",
            f"**Gesamtstatus:** technische Ausfuehrung `{manifest.get('experiment_status', 'unknown')}`, Tick-Vertrag `{tick_contract}`, semantische Zuordnung `{semantic_status}`, wissenschaftliche Evidenz `false` bis zur menschlichen Review/Freigabe.",
            "",
        ]
    )

    summary_path = experiment_dir / "summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return f"experiments/{experiment_id}/summary.md"
