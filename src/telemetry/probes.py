from src.core.spatial_index import unpack_coords


class ProbeManager:
    def __init__(self, network, config=None):
        self.network = network
        self.probes: list[int] = []

    def add_probe(self, neuron_id: int) -> None:
        if neuron_id in self.network.neurons and neuron_id not in self.probes:
            self.probes.append(neuron_id)

    def remove_probe(self, neuron_id: int) -> None:
        if neuron_id in self.probes:
            self.probes.remove(neuron_id)

    def get_probe_data(self, neuron_id: int) -> dict:
        neuron = self.network.neurons.get(neuron_id)
        if neuron is None:
            return {}
        return {
            "neuron_id": neuron_id,
            "coord": unpack_coords(neuron_id),
            "v": neuron.v,
            "u": neuron.u,
            "energy": neuron.energy,
            "spike_counter": neuron.spike_counter,
            "last_spike_tick": neuron.last_spike_tick,
            "incoming": self.network.in_degree.get(neuron_id, 0),
            "outgoing": len(self.network.synapses.get(neuron_id, [])),
            "last_external_current": neuron.last_external_current,
            "last_synaptic_current": neuron.last_synaptic_current,
        }
