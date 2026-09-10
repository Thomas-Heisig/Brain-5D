"""Finalize the initial publication; never overwrite earlier scientific records."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def replace(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise ValueError(f'Unexpected source in {path}')
    target.write_text(text.replace(old, new), encoding='utf-8')


def source_repairs() -> None:
    replace('src/experiments/learning_lab.py',
        '    condition: str = "learning_on"',
        '''    condition: str = "learning_on"
    # Partition counts declare a design, not executed validation episodes.
    partition_counts_are_declared: bool = True
    validation_episodes_executed: int = 0
    holdout_episodes_executed: int = 0
    baseline_probes_executed: int = 1
    post_training_probes_executed: int = 1''')
    replace('src/research/followup_experiments.py',
        '                            "probe_after_training_only": True,',
        '''                            "probe_after_training_only": True,
                            "partition_counts_are_declared": True,
                            "validation_episodes_executed": 0,
                            "holdout_episodes_executed": 0,
                            "baseline_probes_executed": 1,
                            "post_training_probes_executed": 1,''')
    replace('src/dashboard/experiment_workflow.py',
        '        exact_window_runners = {',
        '        exact_window_runners = {\n            "run_eval_dimensional",')
    replace('tests/test_mhrn_naming.py',
        '(ROOT / identity["publication"]["path"] / "manifest.json").read_text(',
        '(ROOT / "research/publications/2026-09-08_recursive-epistemics_v1.3/manifest.json").read_text(')
    replace('pyproject.toml', '[project.optional-dependencies]',
        '[project.optional-dependencies]\nempirical = ["brian2==2.10.1"]')
    replace('scripts/empirical_campaign.py',
        '        f"EXP-EMP-20260910-{index + 1:03d}", output_dir=folder',
        '        f"{plan[\"campaign\"]}-{index + 1:03d}", output_dir=folder')
    replace('.pre-commit-config.yaml',
        '        # Delivered publication sizes are enforced by the SHA-256 manifest test.\n        exclude: ^research/publications/',
        '''        # Publication and these two immutable trace sizes/hashes are checked
        # by empirical-data-integrity. All other paths retain the 500 KiB cap.
        exclude: ^(research/publications/|research/experiments/EXP-EMP-20260910/(024-embodied_timing_v1|027-brian2_single_neuron_v1)/runs\\.json\\.gz$)''')


def publication_notes(original: Path, amended: Path) -> None:
    from scripts import publication_empirical as pub

    pub.publish(original, amended)
    folder = ROOT / 'research/publications' / pub.EDITION
    notes = '''

## Messgrenzen der Skalierung und Kennungen

Die v2-Serie umfasst tatsaechlich 15 Laeufe (fuenf Groessen, drei Seeds), alle mit endlichen Zustaenden. 100000 Neuronen und 400000 Kanten: im Mittel 2,00273 Ticks/s, beobachtete Spannweite 1,96761 bis 2,04618; jeweils nur 32 Ticks. Aufbauzeit im Mittel 4,81914 s; RSS nach dem Lauf im Mittel 436365995 Bytes (rund 416,15 MiB), ohne daraus isolierten Netzspeicher abzuleiten.

Die fuenf Groessen laufen pro Seed im selben Prozess. Speicherallokatoren koennen Speicher aus der vorherigen grossen Instanz behalten; daher sind die RSS-Werte kleinerer Instanzen in spaeteren Seeds deutlich hoeher. Diese Werte erlauben keine saubere Speicherskalierungskurve. Nur acht Quellen werden zweimal angeregt; die Aktivitaetsdichte wird nicht proportional zur Netzgroesse konstant gehalten. Die identische Spike-/Ereigniszahl der groessten zwei Instanzen stuetzt keinen dicht aktiven Durchsatznachweis.

Der aufgezeichnete v2-Kindmanifestname lautet aufgrund eines Metadatenfehlers noch EXP-EMP-20260910-001. Er ist ohne Kampagnenpfad nicht eindeutig. Unveraenderte Originalmanifeste bleiben erhalten; campaign-index.json bietet qualifizierte Referenzen aus Kampagne und Unterverzeichnis. Kuenftige Ausfuehrungen verwenden den deklarierten campaign-id-Praefix. Die Reparatur veraendert weder alte Messwerte noch deren Quellbindung.

Die Kampagnenindex-Manifeste sind nachtraegliche Navigationsmetadaten. Sie sind keine neuen Messlaeufe, keine eigenen unabhaengigen Replikationen und nicht zur automatischen Evidenzfreigabe geeignet. Alle unveraenderten Kindmanifeste, Rohdaten und Eingabeplaene bleiben ueber ihre SHA-256-Pruefsummen nachvollziehbar.
'''
    p = folder / 'section-058.md'
    p.write_text(p.read_text(encoding='utf-8') + notes, encoding='utf-8')
    p = ROOT / 'research/experiments/EXP-EMP-20260910/ANALYSIS.md'
    p.write_text(p.read_text(encoding='utf-8') + notes, encoding='utf-8')
    for name in pub.CAMPAIGNS:
        directory = ROOT / 'research/experiments' / name
        plan = pub.load(directory / 'plan.json')
        summary = pub.load(directory / 'summary.json')
        records = []
        for row in summary['protocols']:
            child = Path(row['data']).parent
            records.append({'qualified_record_id': name + '/' + child.as_posix(),
                            'protocol': row['protocol'], 'status': row['status'],
                            'runs': row['runs'], 'manifest': (child / 'manifest.json').as_posix(),
                            'raw': row['data']})
        pub.save(directory / 'campaign-index.json', {'campaign': name, 'record_kind': 'navigation_index_not_new_experiment', 'original_child_ids_require_campaign_scope': True, 'records': records, 'accepted_evidence': False})
        base = pub.load(directory / records[0]['manifest'])
        failed = sum(n for status, n in summary['status_counts'].items() if status != 'completed')
        base.update(experiment_id=name, record_kind='campaign_index',
                    experiment_status='failed' if failed else 'completed',
                    validity={'valid': False, 'reason': 'Aggregate navigation index; assess original child runs separately', 'runtime_error_count': failed, 'fatal_error_count': 0},
                    simulation={'campaign_plan': 'plan.json', 'stored_run_count': summary['total_runs']},
                    research_questions=sorted({s['research_question'] for s in plan['selections'] if s['research_question']}),
                    hypotheses=sorted({s['hypothesis'] for s in plan['selections'] if s['hypothesis']}),
                    artifacts={'summary': 'summary.json', 'report': 'REPORT.md', 'index': 'campaign-index.json'},
                    results={'execution_states': summary['status_counts'], 'stored_run_count': summary['total_runs'], 'accepted_evidence': False, 'analysis_ai_assisted': True},
                    original_provenance_in_child_manifests=True, automatic_evidence_promotion=False)
        # Do not reuse the first child's freeze digest as the index's provenance.
        base.pop('source_freeze_sha', None)
        base.pop('provenance_digests', None)
        base['index_provenance'] = {'source_commit': summary['source'], 'source_digest': summary['source_digest'], 'summary_sha256': pub.sha(directory / 'summary.json')}
        pub.save(directory / 'manifest.json', base)
        pub.save(directory / 'ARTIFACTS.json', {'files_sha256': pub.inventory(directory), 'source_commit': summary['source'], 'accepted_evidence': False, 'original_data_unchanged': True})
    p = folder / 'MANUSCRIPT.md'
    text = p.read_text(encoding='utf-8')
    p.write_text(text + notes, encoding='utf-8')
    manifest = pub.load(folder / 'manifest.json')
    manifest['files'] = {p.name: {'sha256': pub.sha(p), 'size': p.stat().st_size} for p in folder.iterdir() if p.is_file() and p.name != 'manifest.json'}
    pub.save(folder / 'manifest.json', manifest)
    pub.verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path)
    parser.add_argument('--amended', required=True, type=Path)
    args = parser.parse_args()
    source_repairs()
    publication_notes(args.original, args.amended)
