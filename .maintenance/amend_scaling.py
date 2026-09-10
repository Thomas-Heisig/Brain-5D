"""One-time, reviewable addressing repair; never changes historical observations."""
from pathlib import Path
import json
import yaml

ROOT = Path(__file__).resolve().parents[1]

def replace_once(path, old, new):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    if text.count(old) != 1:
        raise ValueError(f'Unexpected source for {path}')
    target.write_text(text.replace(old, new), encoding='utf-8')

replace_once('src/research/empirical_evaluation.py',
    '    values["dimensions"] = [neurons, 1, 1, 1, 1]',
    '''    if not 1 <= neurons <= 256**5:
        raise ValueError("Neuron count exceeds the canonical five-axis ID space")
    # Canonical persisted IDs allocate eight bits to each coordinate.
    values["dimensions"] = [
        min(256, max(1, (neurons + 256**axis - 1) // 256**axis))
        for axis in range(5)
    ]''')
replace_once('src/research/empirical_evaluation.py',
    '    ids = [net.add_neuron((index, 0, 0, 0, 0)) for index in range(neurons)]',
    '''    ids = [
        net.add_neuron((index % 256, (index // 256) % 256,
                        (index // 256**2) % 256, (index // 256**3) % 256,
                        (index // 256**4) % 256))
        for index in range(neurons)
    ]''')
replace_once('src/research/empirical_evaluation.py',
    '                "synapses": count * 4,',
    '                "synapses": count * 4,\n                "address_encoding": "canonical_5d_base256_v2",\n                "coordinate_repair_not_nd_migration": True,')
p = ROOT / 'src/research/followup_experiments.py'
p.write_text(p.read_text() + '''

def run_eval_scaling_v2(
    config: Mapping[str, Any], seeds: tuple[int, ...] = (21001, 21002, 21003)
) -> list[ScientificRun]:
    """Addressing-only amendment; the original failed v1 receipt is retained."""
    from .empirical_evaluation import run_active_scaling

    return run_active_scaling(config, seeds)
''')
replace_once('src/research/protocol_registry.py',
    '        "active_scaling_v1": "run_eval_scaling",',
    '        "active_scaling_v1": "run_eval_scaling",\n        "active_scaling_v2": "run_eval_scaling_v2",')
p = ROOT / 'research/preregistrations/operational/active_scaling_v1.json'
record = json.loads(p.read_text())
record.update(preregistration_id='PREREG-RQ-EVAL-005', protocol_id='active_scaling_v2',
              research_question='RQ-EVAL-005', hypothesis='H-EVAL-005-A')
record['seed_strategy']['seeds'] = [21001, 21002, 21003]
record['amendment'] = {
    'previous_source_commit': 'f9ed3c2153858b14face0b1d8410741c662fb028',
    'previous_attempt': 'EXP-EMP-20260910/028-active_scaling_v1/receipt.json',
    'reason': 'Coordinate 256 exceeded the canonical 0..255 per-axis bound; no v1 scaling result list was returned.',
    'change': 'Decompose linear indices into five base256 coordinates. Same active workload and thresholds; fresh seeds21001..21003. No persistence migration.',
    'previous_attempt_retained': True,
    'outcome_based_threshold_change': False,
}
(p.parent / 'active_scaling_v2.json').write_text(json.dumps(record, indent=2) + '\n')
p = ROOT / 'research/protocols/empirical.operational.json'
item = json.loads(p.read_text())['protocols'][-1].copy()
item.update(id='active_scaling_v2', research_question='RQ-EVAL-005', hypothesis='H-EVAL-005-A',
            preregistration='preregistrations/operational/active_scaling_v2.json')
(p.parent / 'empirical-amendment.operational.json').write_text(json.dumps({
    'schema_version': '1.0', 'program': 'addressing-amendment-v2', 'protocols': [item]}, indent=2) + '\n')
for kind in ['questions', 'hypotheses']:
    p = ROOT / f'research/registry/{kind}.empirical.yaml'
    entries = yaml.safe_load(p.read_text())
    item = entries[-1].copy()
    if kind == 'questions':
        item.update(id='RQ-EVAL-005', hypotheses=['H-EVAL-005-A'],
                    question='Does corrected canonical base256 addressing execute the declared active-scaling workload through100000 neurons without changing graph budgets?')
    else:
        item.update(id='H-EVAL-005-A', research_question='RQ-EVAL-005')
    entries.append(item)
    p.write_text(yaml.safe_dump(entries, sort_keys=False))
replace_once('scripts/empirical_campaign.py', 'def execute(output: Path) -> None:',
             'def execute(output: Path, protocols: list[str] | None = None, campaign: str = "EXP-EMP-20260910") -> None:')
replace_once('scripts/empirical_campaign.py', '    plan = make_plan()\n    save(output / "plan.json", plan)',
    '''    plan = make_plan()
    plan["campaign"] = campaign
    if protocols:
        known = {item["protocol"] for item in plan["selections"]}
        if set(protocols) - known:
            raise ValueError("Unknown or human-review-only selected protocol")
        plan["not_selected_protocols"] = sorted(known - set(protocols))
        plan["selections"] = [item for item in plan["selections"] if item["protocol"] in protocols]
        plan["selection_scope"] = "explicitly selected amendment; not a full rerun"
    save(output / "plan.json", plan)''')
replace_once('scripts/empirical_campaign.py', '    parser.add_argument("--worker", type=int)',
    '    parser.add_argument("--worker", type=int)\n    parser.add_argument("--protocol", action="append")\n    parser.add_argument("--campaign-id", default="EXP-EMP-20260910")')
replace_once('scripts/empirical_campaign.py', '        execute(args.output)',
             '        execute(args.output, args.protocol, args.campaign_id)')
p = ROOT / 'tests/test_empirical_evaluation.py'
p.write_text(p.read_text() + '''

def test_canonical_coordinate_boundary_repair() -> None:
    from src.core.spatial_index import unpack_coords
    from src.research.empirical_evaluation import _network

    net, ids = _network({}, 1024, 7)
    assert len(set(ids)) == len(net.neurons) == 1024
    assert unpack_coords(ids[255]) == (255, 0, 0, 0, 0)
    assert unpack_coords(ids[256]) == (0, 1, 0, 0, 0)
    assert unpack_coords(ids[1023]) == (255, 3, 0, 0, 0)
''')
