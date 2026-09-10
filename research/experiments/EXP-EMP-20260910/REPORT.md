# Empirical campaign: executed DATA, not accepted EVID

Source: `f9ed3c2153858b14face0b1d8410741c662fb028`; digest `bac59880cc48e43f315b768750c00cdfabcb97180f04a1b25103d603b6308fd5`.

AI-assisted design/analysis; zero runtime model calls. No independent replication or ethics approval asserted.

| Protocol | Execution | Runs |
| --- | --- | ---: |
| recurrence_map_v1 | completed | 300 |
| learning_generalization_v1 | completed | 180 |
| independent_replication_v1 | completed | 40 |
| topology_matched_5d_v1 | completed | 120 |
| closed_loop_regulation_v1 | completed | 40 |
| temporal_order_spiking_v1 | completed | 60 |
| subsystem_performance_v1 | completed | 10 |
| recurrence_scale_v1 | completed | 80 |
| learning_interference_screen_v1 | completed | 20 |
| sustained_activity_stability_v1 | completed | 20 |
| msba_energy_efficiency_v1 | completed | 9 |
| msba_resource_allocation_v1 | completed | 9 |
| msba_visual_roi_v1 | completed | 12 |
| msba_digital_integrity_v1 | completed | 9 |
| msba_modality_compensation_v1 | completed | 12 |
| memory_delayed_information_v1 | completed | 12 |
| world_model_prediction_v1 | completed | 12 |
| behavior_profile_control_v1 | completed | 12 |
| embodied_closed_loop_v1 | completed | 9 |
| embodied_proprioception_v1 | completed | 12 |
| embodied_perturbation_screen_v1 | completed | 12 |
| connectome_topology_screen_v1 | completed | 12 |
| embodied_controller_attribution_v1 | completed | 12 |
| embodied_timing_v1 | completed | 21 |
| dimensional_connectivity_v1 | completed | 130 |
| native_association_holdout_v1 | completed | 50 |
| brian2_single_neuron_v1 | completed | 3 |
| active_scaling_v1 | failed | 0 |
| foundational_seven_suite | completed | 54 |

Human review templates not executed: 22.

## Scope and inference

Engineering completion is not scientific success. Constant outcomes across seeds do not establish independent empirical variation. The legacy matched-5D protocol preserves one graph and measures embedding invariance. Local seeded replication is not an external team's replication. Component memory, world-model and profile experiments are not SNN-learning evidence. Real human reviews remain pending.

New topology contrasts measure propagation, not task advantage. The teacher-paired native association task is synthetic; test weights are frozen, evaluation episodes are novel, and teacher current is absent during all tests. Brian2 covers matched single-cell integration only, not framework superiority. Scaling is a short active sparse workload; RSS samples are not isolated memory peaks and no electrical energy is measured.

New inferential comparisons use paired simulation seeds, 2000 fixed-seed percentile bootstraps, exact two-sided sign flips and Holm correction per family; n is small and the sign-flip symmetry assumption is not empirically guaranteed. Degenerate effects have no invented standardized effect size. No automatic EVID promotion.

## Declared comparisons

```json
{
  "dimensional_connectivity_v1": [
    {
      "reference": "geometry_5d",
      "control": "geometry_2d",
      "metric": "output_spikes",
      "n_seed_pairs": 10,
      "mean_difference": 5.0,
      "bootstrap_percentile_95_ci": [
        -2.4,
        11.7
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.234375,
      "paired_standardized_effect_dz": 0.40734408494517627,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 1.0
    },
    {
      "reference": "geometry_5d",
      "control": "geometry_3d",
      "metric": "output_spikes",
      "n_seed_pairs": 10,
      "mean_difference": -3.0,
      "bootstrap_percentile_95_ci": [
        -9.4,
        4.6
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.462890625,
      "paired_standardized_effect_dz": -0.2467838236981868,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 1.0
    },
    {
      "reference": "geometry_5d",
      "control": "geometry_4d",
      "metric": "output_spikes",
      "n_seed_pairs": 10,
      "mean_difference": 2.4,
      "bootstrap_percentile_95_ci": [
        -2.9,
        7.7
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.421875,
      "paired_standardized_effect_dz": 0.2617922202406517,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 1.0
    },
    {
      "reference": "geometry_5d",
      "control": "geometry_6d",
      "metric": "output_spikes",
      "n_seed_pairs": 10,
      "mean_difference": 0.3,
      "bootstrap_percentile_95_ci": [
        -4.5,
        4.8
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.921875,
      "paired_standardized_effect_dz": 0.037562002391902015,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 1.0
    },
    {
      "reference": "geometry_5d",
      "control": "geometry_8d",
      "metric": "output_spikes",
      "n_seed_pairs": 10,
      "mean_difference": 2.8,
      "bootstrap_percentile_95_ci": [
        -3.4,
        9.6
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.46875,
      "paired_standardized_effect_dz": 0.2411245899885896,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 1.0
    }
  ],
  "native_association_holdout_v1": [
    {
      "reference": "learning_on",
      "control": "learning_off",
      "metric": "test_accuracy",
      "n_seed_pairs": 10,
      "mean_difference": 0.285,
      "bootstrap_percentile_95_ci": [
        0.2,
        0.37
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.001953125,
      "paired_standardized_effect_dz": 1.9474616822651607,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 0.0078125
    },
    {
      "reference": "learning_on",
      "control": "sham_replay",
      "metric": "test_accuracy",
      "n_seed_pairs": 10,
      "mean_difference": 0.285,
      "bootstrap_percentile_95_ci": [
        0.2,
        0.37
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.001953125,
      "paired_standardized_effect_dz": 1.9474616822651607,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 0.0078125
    },
    {
      "reference": "learning_on",
      "control": "weight_reset",
      "metric": "test_accuracy",
      "n_seed_pairs": 10,
      "mean_difference": 0.285,
      "bootstrap_percentile_95_ci": [
        0.2,
        0.37
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.001953125,
      "paired_standardized_effect_dz": 1.9474616822651607,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 0.0078125
    },
    {
      "reference": "learning_on",
      "control": "weight_shuffle",
      "metric": "test_accuracy",
      "n_seed_pairs": 10,
      "mean_difference": 0.285,
      "bootstrap_percentile_95_ci": [
        0.2,
        0.37
      ],
      "bootstrap_resamples": 2000,
      "bootstrap_seed": 910,
      "exact_two_sided_sign_flip_p": 0.001953125,
      "paired_standardized_effect_dz": 1.9474616822651607,
      "degenerate_difference_variance": false,
      "unit": "independent_environment_and_initialization_seed",
      "interpretation": "exploratory; no automatic hypothesis or EVID acceptance",
      "holm_adjusted_p": 0.0078125
    }
  ]
}
```

## Questions without a matching runnable protocol

RQ-5D-001, RQ-5D-002, RQ-5D-003, RQ-5D-004, RQ-AIR-001, RQ-CONN-001, RQ-DET-001, RQ-EMB-003, RQ-EMB-007, RQ-EMB-008, RQ-EPIST-001, RQ-ETH-001, RQ-ETH-002, RQ-GW-001, RQ-GW-002, RQ-GW-003, RQ-GW-004, RQ-GW-005, RQ-GW-006, RQ-GW-007, RQ-HOM-001, RQ-HOM-002, RQ-LLM-001, RQ-MEM-001, RQ-PING-001, RQ-REG-001, RQ-SCALE-001, RQ-SELF-001, RQ-SELF-002, RQ-SNN-002, RQ-SNN-003, RQ-SNN-004, RQ-SNN-005, RQ-STDP-001, RQ-STDP-002, RQ-STORAGE-001, RQ-STORAGE-002, RQ-STORAGE-003, RQ-STORAGE-004, RQ-STRUCT-001, RQ-SUITE-001, RQ-TEMP-001, RQ-TIME-001

These are not replaced by generic tick runs. External assessment, unavailable adapters, independent teams and additional framework integrations cannot be manufactured by this campaign.
