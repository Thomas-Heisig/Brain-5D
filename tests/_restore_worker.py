"""Restore worker subprocess for Path C."""
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
from typing import Any

def _canonical_state_digest(network, homeostasis=None, learning=None):
    import hashlib
    d = hashlib.sha256()
    d.update(str(network.current_tick).encode())
    d.update(str(network.total_spikes).encode())
    d.update(str(network.total_events_processed).encode())
    rv, rs, rg = network.rng.getstate()
    d.update(str(rv).encode() + str(rs).encode() + str(rg).encode())
    for nid in sorted(network.pending_currents):
        d.update(str(nid).encode() + str(network.pending_currents[nid]).encode())
    for nid in sorted(network.input_cells):
        d.update(str(nid).encode())
    for nid in sorted(network.output_cells):
        d.update(str(nid).encode())
    evs = []
    for slot in network.event_slots:
        for ev in slot:
            evs.append((ev.delivery_tick, ev.source_id, ev.target_id, ev.weight))
    for dt, src, tgt, w in sorted(evs):
        d.update(str(dt).encode() + str(src).encode() + str(tgt).encode() + str(w).encode())
    for nid in sorted(network.neurons):
        n = network.neurons[nid]
        for f in [n.v, n.u, n.energy, n.spike_counter, n.last_spike_tick,
                   n.threshold_adaptation, n.a, n.b, n.c, n.d, n.spike_cost]:
            d.update(str(f).encode())
    sd = []
    for src_id in sorted(network.synapses):
        for syn in network.synapses[src_id]:
            sd.append((src_id, syn.target_id, syn.weight, syn.delay, syn.eligibility, syn.last_pre_spike))
    for _s, tgt, w, dl, el, lps in sorted(sd):
        d.update(str(tgt).encode() + str(w).encode() + str(dl).encode() + str(el).encode() + str(lps).encode())
    if homeostasis is not None and hasattr(homeostasis, "_rates_hz"):
        for nid in sorted(homeostasis._rates_hz):
            d.update(str(nid).encode() + str(homeostasis._rates_hz[nid]).encode())
    if learning is not None:
        for key in sorted(learning._states):
            s = learning._states[key]
            d.update(str(s.pre_id).encode() + str(s.synapse.target_id).encode() + str(s.last_pre_tick).encode() + str(s.last_post_tick).encode() + str(s.eligibility.value).encode())
        for r in learning._pending_rewards:
            d.update(str(r.value).encode() + str(r.tick).encode())
    return d.hexdigest()

def _run_schedule(network, schedule, end_tick):
    sm = {}
    for entry in schedule:
        t = int(entry["tick"])
        if t < end_tick:
            ids = entry["neuron_ids"]
            curr = float(entry["current"])
            sm[t] = [(nid, curr) for nid in ids]
    while network.current_tick < end_tick:
        tick = network.current_tick
        if tick in sm:
            for nid, curr in sm[tick]:
                network.inject_current(nid, curr)
        network.step()

def main():
    import argparse, json, sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--schedule", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--end-tick", type=int, required=True)
    args = parser.parse_args()

    from src.storage.core_restore import restore_full
    bundle = restore_full(
        snapshot_path=Path(args.snapshot),
        journal_path=Path(args.journal),
        checkpoint_path=Path(args.checkpoint),
        config=json.loads(Path(args.config).read_text()),
        recovered_path=Path(args.output).parent / "recovered.b5d",
        create_homeostasis_engine=True,
        create_learning_engine=True,
    )
    schedule = json.loads(Path(args.schedule).read_text())
    _run_schedule(bundle.network, schedule, args.end_tick)
    digest = _canonical_state_digest(bundle.network, bundle.homeostasis_engine, bundle.learning_engine)
    result = {"digest": digest, "pid": os.getpid()}
    Path(args.output).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Worker done: digest={digest}, pid={os.getpid()}")

if __name__ == "__main__":
    main()
