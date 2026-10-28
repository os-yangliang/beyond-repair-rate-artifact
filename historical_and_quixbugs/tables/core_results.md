# Rebuilt article results

Recomputed from sanitized identity-level outcome metadata. No model, candidate, or test is run.

## Original Refactory studies

| Dataset | Service | Timepoint | Contract | Policy | Complete / N | UNKNOWN |
|---|---|---|---|---|---:|---:|
| study_1 | Qwen | final_delivery | original | TEMP | 12/17 | 0 |
| study_1 | Qwen | final_delivery | original | FREE | 14/17 | 0 |
| study_2 | Qwen | final_delivery | original | SOFT | 6/9 | 0 |
| study_2 | Qwen | final_delivery | original | REGION | 6/9 | 0 |
| study_2 | Qwen | final_delivery | original | FREE | 5/9 | 0 |
| study_3 | Qwen | final_delivery | original | SEED | 9/14 | 0 |
| study_3 | Qwen | final_delivery | original | CLOSURE | 9/14 | 0 |
| study_3 | Qwen | final_delivery | original | FULL | 9/14 | 0 |

These three developmental populations share assignment families and are not pooled.

## Original external repair trajectories

| Dataset | Service | Timepoint | Contract | Policy | Complete / N | UNKNOWN |
|---|---|---|---|---|---:|---:|
| external_qwen | Qwen | first_opportunity | original | SEED | 8/10 | 0 |
| external_qwen | Qwen | first_opportunity | original | CLOSURE | 10/10 | 0 |
| external_qwen | Qwen | first_opportunity | original | FULL | 10/10 | 0 |
| external_qwen | Qwen | final_delivery | original | SEED | 10/10 | 0 |
| external_qwen | Qwen | final_delivery | original | CLOSURE | 10/10 | 0 |
| external_qwen | Qwen | final_delivery | original | FULL | 10/10 | 0 |
| external_kimi | Kimi | first_opportunity | original | SEED | 5/10 | 0 |
| external_kimi | Kimi | first_opportunity | original | CLOSURE | 7/10 | 0 |
| external_kimi | Kimi | first_opportunity | original | FULL | 8/10 | 0 |
| external_kimi | Kimi | final_delivery | original | SEED | 7/10 | 0 |
| external_kimi | Kimi | final_delivery | original | CLOSURE | 7/10 | 0 |
| external_kimi | Kimi | final_delivery | original | FULL | 8/10 | 0 |

The services use the same ten inputs; repeated arms and services do not create new tasks.

## Archived first-response formatting diagnostic

| Dataset | Service | Timepoint | Contract | Policy | Complete / N | UNKNOWN |
|---|---|---|---|---|---:|---:|
| format_first_response | Qwen | fixed_first_response | original | SEED | 8/10 | 0 |
| format_first_response | Qwen | fixed_first_response | original | CLOSURE | 10/10 | 0 |
| format_first_response | Qwen | fixed_first_response | original | FULL | 10/10 | 0 |
| format_first_response | Qwen | fixed_first_response | normalized | SEED | 8/10 | 0 |
| format_first_response | Qwen | fixed_first_response | normalized | CLOSURE | 10/10 | 0 |
| format_first_response | Qwen | fixed_first_response | normalized | FULL | 10/10 | 0 |
| format_first_response | Kimi | fixed_first_response | original | SEED | 5/10 | 0 |
| format_first_response | Kimi | fixed_first_response | original | CLOSURE | 7/10 | 0 |
| format_first_response | Kimi | fixed_first_response | original | FULL | 8/10 | 0 |
| format_first_response | Kimi | fixed_first_response | normalized | SEED | 8/10 | 0 |
| format_first_response | Kimi | fixed_first_response | normalized | CLOSURE | 9/10 | 0 |
| format_first_response | Kimi | fixed_first_response | normalized | FULL | 10/10 | 0 |

The normalized rows concern fixed first responses only. They are not new two-round trajectories,
and do not estimate saved calls or tokens. Original and normalized rows are paired observations.

`identity_outcomes.csv` retains every projected identity, including unsuccessful and UNKNOWN outcomes.
`paired_outcomes.csv` reports paired counts without significance or equivalence claims.

See `input_hashes.json` for both the portable input hashes and original analysis-file hashes.
