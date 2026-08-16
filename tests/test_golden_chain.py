import random
from conftest import base_config
from src.core.network import NeuralNetwork
from src.diagnostics.propagation import PropagationAnalyzer
from src.diagnostics.stimulus import StimulusResult
from src.telemetry.spike_history import SpikeHistory


def test_golden_chain_a_b_c():
    net=NeuralNetwork(base_config(),random.Random(123)); A=net.add_neuron((1,1,1,1,1)); B=net.add_neuron((1,1,1,1,2)); C=net.add_neuron((1,1,1,1,3))
    net.connect(A,B,100.0,2); net.connect(B,C,100.0,3); net.input_cells={A}; net.output_cells={C}
    hist=SpikeHistory(100); analyzer=PropagationAnalyzer(net.output_cells)
    net.inject_current(A,100.0)
    for t in range(6):
        stim=StimulusResult(t,"manual",(A,),(100.0,),100.0) if t==0 else StimulusResult(t,"none",(),(),0.0)
        r=net.step(); hist.append(r.tick,r.spike_ids); analyzer.observe(stim,r)
    assert hist.get_spikes_for_tick(0)==(A,); assert hist.get_spikes_for_tick(2)==(B,); assert hist.get_spikes_for_tick(5)==(C,)
    report=analyzer.get_report(); assert report.secondary_recruited_count==2; assert report.first_secondary_tick==2; assert report.output_reached; assert report.first_output_tick==5
