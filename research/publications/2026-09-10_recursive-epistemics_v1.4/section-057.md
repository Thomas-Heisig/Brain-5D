# Ausfuehrungsbilanz und zentrale Messgroessen

EXP-EMP-20260910: {'completed': 28, 'failed': 1}; 1272 gespeicherte Laeufe; Quellcommit `f9ed3c2153858b14face0b1d8410741c662fb028`; Eingabedigest `bac59880cc48e43f315b768750c00cdfabcb97180f04a1b25103d603b6308fd5`.

EXP-EMP-20260910-SCALE-V2: {'completed': 1}; 15 gespeicherte Laeufe; Quellcommit `a0652860d28a2fd237ad385efb533159e56a9318`; Eingabedigest `aba99e52418d07251aa51906ebb3813b984a81791563979b9b31cecae60ce58e`.

| Protokoll / Bedingung | n | Messgroesse | Mittel | Minimum | Maximum |
| --- | ---: | --- | ---: | ---: | ---: |
| dimensional_connectivity_v1 / fixed_graph_label_2d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / fixed_graph_label_3d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / fixed_graph_label_4d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / fixed_graph_label_5d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / fixed_graph_label_6d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / fixed_graph_label_8d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / geometry_2d | 10 | output_spikes | 72.4 | 60 | 83 |
| dimensional_connectivity_v1 / geometry_3d | 10 | output_spikes | 80.4 | 63 | 101 |
| dimensional_connectivity_v1 / geometry_4d | 10 | output_spikes | 75 | 62 | 90 |
| dimensional_connectivity_v1 / geometry_5d | 10 | output_spikes | 77.4 | 66 | 94 |
| dimensional_connectivity_v1 / geometry_6d | 10 | output_spikes | 77.1 | 59 | 99 |
| dimensional_connectivity_v1 / geometry_8d | 10 | output_spikes | 74.6 | 61 | 90 |
| dimensional_connectivity_v1 / random_graph | 10 | output_spikes | 69.6 | 40 | 92 |
| native_association_holdout_v1 / learning_off | 10 | test_accuracy | 0.5 | 0.5 | 0.5 |
| native_association_holdout_v1 / learning_on | 10 | test_accuracy | 0.785 | 0.575 | 1 |
| native_association_holdout_v1 / sham_replay | 10 | test_accuracy | 0.5 | 0.5 | 0.5 |
| native_association_holdout_v1 / weight_reset | 10 | test_accuracy | 0.5 | 0.5 | 0.5 |
| native_association_holdout_v1 / weight_shuffle | 10 | test_accuracy | 0.5 | 0.5 | 0.5 |
| brian2_single_neuron_v1 / matched_split_euler | 3 | max_abs_voltage_error | 99.5811 | 99.5811 | 99.5811 |
| active_scaling_v2 / n100000 | 3 | ticks_per_second | 2.00273 | 1.96761 | 2.04618 |
| active_scaling_v2 / n1024 | 3 | ticks_per_second | 384.374 | 374.978 | 397.499 |
| active_scaling_v2 / n128 | 3 | ticks_per_second | 3005.18 | 2874.17 | 3080.78 |
| active_scaling_v2 / n25000 | 3 | ticks_per_second | 10.616 | 10.5467 | 10.7195 |
| active_scaling_v2 / n5000 | 3 | ticks_per_second | 69.1581 | 64.634 | 72.7422 |

## Vorab deklarierte gepaarte Vergleiche

| Referenz minus Kontrolle | n | Differenz | 95%-Bootstrapintervall | p exakt | p Holm |
| --- | ---: | ---: | --- | ---: | ---: |
| geometry_5d - geometry_2d | 10 | 5 | [-2.4, 11.7] | 0.234375 | 1 |
| geometry_5d - geometry_3d | 10 | -3 | [-9.4, 4.6] | 0.462891 | 1 |
| geometry_5d - geometry_4d | 10 | 2.4 | [-2.9, 7.7] | 0.421875 | 1 |
| geometry_5d - geometry_6d | 10 | 0.3 | [-4.5, 4.8] | 0.921875 | 1 |
| geometry_5d - geometry_8d | 10 | 2.8 | [-3.4, 9.6] | 0.46875 | 1 |
| learning_on - learning_off | 10 | 0.285 | [0.2, 0.37] | 0.00195312 | 0.0078125 |
| learning_on - sham_replay | 10 | 0.285 | [0.2, 0.37] | 0.00195312 | 0.0078125 |
| learning_on - weight_reset | 10 | 0.285 | [0.2, 0.37] | 0.00195312 | 0.0078125 |
| learning_on - weight_shuffle | 10 | 0.285 | [0.2, 0.37] | 0.00195312 | 0.0078125 |

## Primarmessungen je Protokoll

n bezeichnet gespeicherte Laeufe, nicht automatisch unabhaengige inferentielle Einheiten. Zahlen: Mittel [Minimum;Maximum]; Boolean: true/n. Vollstaendige strukturierte Messungen stehen in den Rohdaten.

### recurrence_map_v1

Ausfuehrung: completed; 300 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| w0_d1 | 20 | last_response_latency: 2 [2;2]; recurrent_events: 0 [0;0]; propagation_depth: 1 [1;1]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w0_d2 | 20 | last_response_latency: 2 [2;2]; recurrent_events: 0 [0;0]; propagation_depth: 1 [1;1]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w0_d4 | 20 | last_response_latency: 2 [2;2]; recurrent_events: 0 [0;0]; propagation_depth: 1 [1;1]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w100_d1 | 20 | last_response_latency: 62 [62;62]; recurrent_events: 10 [10;10]; propagation_depth: 61 [61;61]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w100_d2 | 20 | last_response_latency: 252 [252;252]; recurrent_events: 33 [33;33]; propagation_depth: 251 [251;251]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w100_d4 | 20 | last_response_latency: 251 [251;251]; recurrent_events: 28 [28;28]; propagation_depth: 250 [250;250]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w125_d1 | 20 | last_response_latency: 84 [84;84]; recurrent_events: 14 [14;14]; propagation_depth: 83 [83;83]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w125_d2 | 20 | last_response_latency: 255 [255;255]; recurrent_events: 34 [34;34]; propagation_depth: 254 [254;254]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w125_d4 | 20 | last_response_latency: 250 [250;250]; recurrent_events: 30 [30;30]; propagation_depth: 249 [249;249]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w50_d1 | 20 | last_response_latency: 7 [7;7]; recurrent_events: 1 [1;1]; propagation_depth: 6 [6;6]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w50_d2 | 20 | last_response_latency: 8 [8;8]; recurrent_events: 1 [1;1]; propagation_depth: 7 [7;7]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w50_d4 | 20 | last_response_latency: 10 [10;10]; recurrent_events: 1 [1;1]; propagation_depth: 9 [9;9]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w75_d1 | 20 | last_response_latency: 25 [25;25]; recurrent_events: 4 [4;4]; propagation_depth: 24 [24;24]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w75_d2 | 20 | last_response_latency: 29 [29;29]; recurrent_events: 4 [4;4]; propagation_depth: 28 [28;28]; persistence_class: strukturiert/kategorial, siehe Rohdaten |
| w75_d4 | 20 | last_response_latency: 57 [57;57]; recurrent_events: 6 [6;6]; propagation_depth: 56 [56;56]; persistence_class: strukturiert/kategorial, siehe Rohdaten |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/001-recurrence_map_v1/runs.json.gz)

### learning_generalization_v1

Ausfuehrung: completed; 180 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| learning_off_drive_0.85 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |
| learning_off_drive_1.00 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |
| learning_off_drive_1.15 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |
| learning_on_drive_0.85 | 20 | generalization_success: 20/20 true; p_success_after: 1 [1;1]; mean_weight_delta: 0.46728 [0.46728;0.46728] |
| learning_on_drive_1.00 | 20 | generalization_success: 20/20 true; p_success_after: 1 [1;1]; mean_weight_delta: 0.46728 [0.46728;0.46728] |
| learning_on_drive_1.15 | 20 | generalization_success: 20/20 true; p_success_after: 1 [1;1]; mean_weight_delta: 0.46728 [0.46728;0.46728] |
| sham_replay_drive_0.85 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |
| sham_replay_drive_1.00 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |
| sham_replay_drive_1.15 | 20 | generalization_success: 0/20 true; p_success_after: 0 [0;0]; mean_weight_delta: 0 [0;0] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/002-learning_generalization_v1/runs.json.gz)

### independent_replication_v1

Ausfuehrung: completed; 40 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| recurrence_off | 20 | total_spikes: 3 [3;3]; recurrent_events: 0 [0;0]; propagation_depth: 1 [1;1]; last_response_latency: 2 [2;2] |
| recurrence_on | 20 | total_spikes: 33 [33;33]; recurrent_events: 10 [10;10]; propagation_depth: 61 [61;61]; last_response_latency: 62 [62;62] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/003-independent_replication_v1/runs.json.gz)

### topology_matched_5d_v1

Ausfuehrung: completed; 120 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| 1d | 30 | first_response_latency: 2 [2;2]; last_response_latency: 2 [2;2]; propagation_depth: 1 [1;1]; total_spikes: 3 [3;3] |
| 2d | 30 | first_response_latency: 2 [2;2]; last_response_latency: 2 [2;2]; propagation_depth: 1 [1;1]; total_spikes: 3 [3;3] |
| 3d | 30 | first_response_latency: 2 [2;2]; last_response_latency: 2 [2;2]; propagation_depth: 1 [1;1]; total_spikes: 3 [3;3] |
| 5d | 30 | first_response_latency: 2 [2;2]; last_response_latency: 2 [2;2]; propagation_depth: 1 [1;1]; total_spikes: 3 [3;3] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/004-topology_matched_5d_v1/runs.json.gz)

### closed_loop_regulation_v1

Ausfuehrung: completed; 40 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| regulation_off | 20 | pressure_phase_spikes: 15 [15;15]; recovery_phase_spikes: 21 [21;21]; recovery_ratio: 1.4 [1.4;1.4] |
| regulation_on | 20 | pressure_phase_spikes: 5 [5;5]; recovery_phase_spikes: 25 [25;25]; recovery_ratio: 5 [5;5] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/005-closed_loop_regulation_v1/runs.json.gz)

### temporal_order_spiking_v1

Ausfuehrung: completed; 60 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| forward | 20 | output_spike_count: 2 [2;2]; total_spikes: 6 [6;6]; sequence_digest: strukturiert/kategorial, siehe Rohdaten |
| reverse | 20 | output_spike_count: 2 [2;2]; total_spikes: 6 [6;6]; sequence_digest: strukturiert/kategorial, siehe Rohdaten |
| simultaneous | 20 | output_spike_count: 1 [1;1]; total_spikes: 3 [3;3]; sequence_digest: strukturiert/kategorial, siehe Rohdaten |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/006-temporal_order_spiking_v1/runs.json.gz)

### subsystem_performance_v1

Ausfuehrung: completed; 10 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| subsystem_profile | 10 | construction_seconds: 0.000149439 [9.9887e-05;0.000460927]; core_step_seconds: 0.0965491 [0.0947481;0.0984389]; digest_seconds: 0.00017208 [0.000155503;0.000193384]; ticks_per_second: 103592 [101586;105543] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/007-subsystem_performance_v1/runs.json.gz)

### recurrence_scale_v1

Ausfuehrung: completed; 80 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| loop_delay_1 | 20 | last_response_latency: 62 [62;62]; recurrent_events: 10 [10;10]; propagation_depth: 61 [61;61] |
| loop_delay_2 | 20 | last_response_latency: 252 [252;252]; recurrent_events: 33 [33;33]; propagation_depth: 251 [251;251] |
| loop_delay_4 | 20 | last_response_latency: 251 [251;251]; recurrent_events: 28 [28;28]; propagation_depth: 250 [250;250] |
| loop_delay_8 | 20 | last_response_latency: 245 [245;245]; recurrent_events: 20 [20;20]; propagation_depth: 244 [244;244] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/008-recurrence_scale_v1/runs.json.gz)

### learning_interference_screen_v1

Ausfuehrung: completed; 20 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| sequential_three_task_screen | 20 | retained_success_fraction: 1 [1;1]; weight_range: 0 [0;0]; task_successes: strukturiert/kategorial, siehe Rohdaten |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/009-learning_interference_screen_v1/runs.json.gz)

### sustained_activity_stability_v1

Ausfuehrung: completed; 20 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| no_input_control | 10 | post_burn_in_spike_cv: 0 [0;0]; post_burn_in_spike_relative_drift: 0 [0;0]; finite_state: 10/10 true; topology_unchanged: 10/10 true |
| tonic_drive | 10 | post_burn_in_spike_cv: 0 [0;0]; post_burn_in_spike_relative_drift: 0 [0;0]; finite_state: 10/10 true; topology_unchanged: 10/10 true |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/010-sustained_activity_stability_v1/runs.json.gz)

### msba_energy_efficiency_v1

Ausfuehrung: completed; 9 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| audio | 3 | normalized_energy_units_per_correct_decision: 19.3943 [18.5628;20.2503]; synaptic_events_per_correct_decision: 16.7167 [16;17.4545]; task_accuracy: 0.958333 [0.916667;1] |
| digital | 3 | normalized_energy_units_per_correct_decision: 10.7748 [10.3128;11.2503]; synaptic_events_per_correct_decision: 8.35837 [8;8.72727]; task_accuracy: 0.958333 [0.916667;1] |
| vision | 3 | normalized_energy_units_per_correct_decision: 45.0963 [43.1628;47.0867]; synaptic_events_per_correct_decision: 41.7918 [40;43.6364]; task_accuracy: 0.958333 [0.916667;1] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/011-msba_energy_efficiency_v1/runs.json.gz)

### msba_resource_allocation_v1

Ausfuehrung: completed; 9 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| adaptive | 3 | task_accuracy: 0.302351 [0.302351;0.302351]; resource_budget_consumed: 66 [66;66]; time_to_budget_exhaustion: 96 [96;96] |
| fixed | 3 | task_accuracy: 0.34375 [0.34375;0.34375]; resource_budget_consumed: 80.4 [80.4;80.4]; time_to_budget_exhaustion: 96 [96;96] |
| random | 3 | task_accuracy: 0.334911 [0.318338;0.344106]; resource_budget_consumed: 77.8207 [73.8071;81.2194]; time_to_budget_exhaustion: 96 [96;96] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/012-msba_resource_allocation_v1/runs.json.gz)

### msba_visual_roi_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| adaptive_roi | 3 | roi_overlap_with_task_relevant_region: 1 [1;1]; task_accuracy: 1 [1;1]; visual_energy_units: 48 [48;48] |
| fixed_center_roi | 3 | roi_overlap_with_task_relevant_region: 0.270833 [0.208333;0.354167]; task_accuracy: 0.270833 [0.208333;0.354167]; visual_energy_units: 192 [192;192] |
| full_image | 3 | roi_overlap_with_task_relevant_region: 1 [1;1]; task_accuracy: 1 [1;1]; visual_energy_units: 768 [768;768] |
| random_roi | 3 | roi_overlap_with_task_relevant_region: 0.0694444 [0.0625;0.0833333]; task_accuracy: 0.0694444 [0.0625;0.0833333]; visual_energy_units: 48 [48;48] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/013-msba_visual_roi_v1/runs.json.gz)

### msba_digital_integrity_v1

Ausfuehrung: completed; 9 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| deterministic_replay | 3 | checksum_mismatches: 0 [0;0]; admitted_symbol_rate: 0.671875 [0.671875;0.671875]; exact_integrity_pass: 3/3 true |
| no_throttling | 3 | checksum_mismatches: 0 [0;0]; admitted_symbol_rate: 1 [1;1]; exact_integrity_pass: 3/3 true |
| throttled | 3 | checksum_mismatches: 0 [0;0]; admitted_symbol_rate: 0.671875 [0.671875;0.671875]; exact_integrity_pass: 3/3 true |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/014-msba_digital_integrity_v1/runs.json.gz)

### msba_modality_compensation_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| adaptive_compensation | 3 | compensatory_gate_change: 0.5 [0.5;0.5]; task_recovery: 0.85 [0.85;0.85]; incremental_energy_cost: 0.1 [0.1;0.1] |
| fixed_allocation | 3 | compensatory_gate_change: 0 [0;0]; task_recovery: 0.425 [0.425;0.425]; incremental_energy_cost: 0 [0;0] |
| no_compensation | 3 | compensatory_gate_change: 0 [0;0]; task_recovery: 0.425 [0.425;0.425]; incremental_energy_cost: -0.35 [-0.35;-0.35] |
| shuffled_utility | 3 | compensatory_gate_change: -0.149487 [-0.408937;0.0330998]; task_recovery: 0.297936 [0.0774039;0.453135]; incremental_energy_cost: -0.484538 [-0.718043;-0.32021] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/015-msba_modality_compensation_v1/runs.json.gz)

### memory_delayed_information_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| memory_read_off | 3 | accuracy: 0.416667 [0.333333;0.541667]; retrievals: 0 [0;0] |
| memory_read_write | 3 | accuracy: 1 [1;1]; retrievals: 24 [24;24] |
| memory_time_shuffled | 3 | accuracy: 0.486111 [0.458333;0.541667]; retrievals: 23 [23;23] |
| memory_write_off | 3 | accuracy: 0.416667 [0.333333;0.541667]; retrievals: 0 [0;0] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/016-memory_delayed_information_v1/runs.json.gz)

### world_model_prediction_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| adaptive | 3 | mean_prediction_error: 0.5 [0.5;0.5] |
| frozen | 3 | mean_prediction_error: 0.5 [0.5;0.5] |
| no_model | 3 | mean_prediction_error: strukturiert/kategorial, siehe Rohdaten |
| persistence | 3 | mean_prediction_error: 0.756944 [0.729167;0.791667] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/017-world_model_prediction_v1/runs.json.gz)

### behavior_profile_control_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| adaptive | 3 | accuracy: 0.566667 [0.55;0.6]; update_count: 40 [40;40] |
| fixed_high_exploration | 3 | accuracy: 0.441667 [0.425;0.475]; update_count: 0 [0;0] |
| fixed_low_exploration | 3 | accuracy: 0.558333 [0.525;0.575]; update_count: 0 [0;0] |
| shuffled_profile | 3 | accuracy: 0.608333 [0.5;0.675]; update_count: 0 [0;0] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/018-behavior_profile_control_v1/runs.json.gz)

### embodied_closed_loop_v1

Ausfuehrung: completed; 9 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| closed_loop | 3 | tracking_rmse_rad: 0.194923 [0.193442;0.196798] |
| feedback_absent | 3 | tracking_rmse_rad: 0.521749 [0.519693;0.524218] |
| yoked_replay | 3 | tracking_rmse_rad: 0.303548 [0.298877;0.307931] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/019-embodied_closed_loop_v1/runs.json.gz)

### embodied_proprioception_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| closed_loop | 3 | tracking_rmse_rad: 0.194923 [0.193442;0.196798] |
| delayed_proprioception | 3 | tracking_rmse_rad: 0.195955 [0.19063;0.203902] |
| feedback_absent | 3 | tracking_rmse_rad: 0.521749 [0.519693;0.524218] |
| timing_shuffle | 3 | tracking_rmse_rad: 0.485494 [0.471601;0.508017] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/020-embodied_proprioception_v1/runs.json.gz)

### embodied_perturbation_screen_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| blocked_joint | 3 | tracking_rmse_rad: 0.372236 [0.36181;0.380647] |
| closed_loop | 3 | tracking_rmse_rad: 0.194923 [0.193442;0.196798] |
| restored_actuator | 3 | tracking_rmse_rad: 0.31707 [0.311963;0.319935] |
| weak_actuator | 3 | tracking_rmse_rad: 0.368636 [0.363304;0.373641] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/021-embodied_perturbation_screen_v1/runs.json.gz)

### connectome_topology_screen_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| degree_preserving | 3 | tracking_rmse_rad: 0.536919 [0.200156;0.724077] |
| random_edges | 3 | tracking_rmse_rad: 0.494167 [0.370308;0.725093] |
| structured | 3 | tracking_rmse_rad: 0.194923 [0.193442;0.196798] |
| weight_shuffle | 3 | tracking_rmse_rad: 0.392802 [0.199118;0.623079] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/022-connectome_topology_screen_v1/runs.json.gz)

### embodied_controller_attribution_v1

Ausfuehrung: completed; 12 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| closed_loop | 3 | tracking_rmse_rad: 0.194923 [0.193442;0.196798] |
| controller_only | 3 | tracking_rmse_rad: 0.230322 [0.226924;0.234234] |
| disconnected_motor | 3 | tracking_rmse_rad: 0.371206 [0.35621;0.3871] |
| shuffled_motor | 3 | tracking_rmse_rad: 0.28634 [0.258364;0.304391] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/023-embodied_controller_attribution_v1/runs.json.gz)

### embodied_timing_v1

Ausfuehrung: completed; 21 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| batch_1 | 3 | batch_digest_identity: 3/3 true |
| batch_128 | 3 | batch_digest_identity: 3/3 true |
| batch_16 | 3 | batch_digest_identity: 3/3 true |
| physics_15ms | 3 | batch_digest_identity: 3/3 true |
| physics_5ms | 3 | batch_digest_identity: 3/3 true |
| sensor_15ms | 3 | batch_digest_identity: 3/3 true |
| sensor_5ms | 3 | batch_digest_identity: 3/3 true |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/024-embodied_timing_v1/runs.json.gz)

### dimensional_connectivity_v1

Ausfuehrung: completed; 130 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| fixed_graph_label_2d | 10 | output_spikes: 77.4 [66;94] |
| fixed_graph_label_3d | 10 | output_spikes: 77.4 [66;94] |
| fixed_graph_label_4d | 10 | output_spikes: 77.4 [66;94] |
| fixed_graph_label_5d | 10 | output_spikes: 77.4 [66;94] |
| fixed_graph_label_6d | 10 | output_spikes: 77.4 [66;94] |
| fixed_graph_label_8d | 10 | output_spikes: 77.4 [66;94] |
| geometry_2d | 10 | output_spikes: 72.4 [60;83] |
| geometry_3d | 10 | output_spikes: 80.4 [63;101] |
| geometry_4d | 10 | output_spikes: 75 [62;90] |
| geometry_5d | 10 | output_spikes: 77.4 [66;94] |
| geometry_6d | 10 | output_spikes: 77.1 [59;99] |
| geometry_8d | 10 | output_spikes: 74.6 [61;90] |
| random_graph | 10 | output_spikes: 69.6 [40;92] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/025-dimensional_connectivity_v1/runs.json.gz)

### native_association_holdout_v1

Ausfuehrung: completed; 50 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| learning_off | 10 | test_accuracy: 0.5 [0.5;0.5] |
| learning_on | 10 | test_accuracy: 0.785 [0.575;1] |
| sham_replay | 10 | test_accuracy: 0.5 [0.5;0.5] |
| weight_reset | 10 | test_accuracy: 0.5 [0.5;0.5] |
| weight_shuffle | 10 | test_accuracy: 0.5 [0.5;0.5] |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/026-native_association_holdout_v1/runs.json.gz)

### brian2_single_neuron_v1

Ausfuehrung: completed; 3 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| matched_split_euler | 3 | conformance_within_1e_8: 0/3 true |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/027-brian2_single_neuron_v1/runs.json.gz)

### active_scaling_v1

Ausfuehrung: failed; 0 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/028-active_scaling_v1/runs.json.gz)

### foundational_seven_suite

Ausfuehrung: completed; 54 gespeicherte Laeufe.

| Bedingung | n | Primaere Beobachtungen |
| --- | ---: | --- |
| 5d:1d | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| 5d:2d | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| 5d:3d | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| 5d:5d | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| 5d:5d_shuffled | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| 5d:random_graph | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| learning:learning_off | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| learning:learning_on | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| learning:sham_replay | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| ping:recurrence_off | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| ping:recurrence_on | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| regulation:chronic_pressure | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| regulation:nominal | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| regulation:telemetry_unknown | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| stdp:productive_reward_stdp | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| temporal:fast_medium_slow | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| time:100 | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |
| time:1000 | 3 | Sieben Basisfamilien; siehe vollstaendige Metriken in summary.json |

[Unveraenderte Originaldaten](../../experiments/EXP-EMP-20260910/029-foundational_seven_suite/runs.json.gz)
