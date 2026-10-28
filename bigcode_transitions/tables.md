# BigCodeBench public-stop transitions and partition strata

This is an arithmetic audit of safe metadata, with no new model, candidate, or test execution. Counts are task–repetition observations unless explicitly marked tasks. Each service has 29 tasks and three within-task repetitions. T* was evaluated after sealing and never controlled continuation.

## First opportunity and decoder accounting

| Service | Public pool | P0 public stop | R1 prepared | R1 actual | R1 local refusal | Decoder accept / reject | R1 public stop: T* pass / fail |
| --- | --- | --- | --- | --- | --- | --- | --- |
| qwen | C0 | 0 | 87 | 87 | 0 | 87 / 0 | 40 / 8 |
| qwen | C1 | 18 | 69 | 69 | 0 | 69 / 0 | 24 / 9 |
| kimi | C0 | 0 | 87 | 84 | 3 | 38 / 46 | 24 / 2 |
| kimi | C1 | 18 | 69 | 66 | 3 | 35 / 31 | 18 / 5 |

## Release reconstruction

| Service | Pool | First T* pass | First T* fail | P0 stop T* fail | R1 public stop T* fail | Prepared R2 | Actual R2 | Local R2 refusal | Final T* pass: retained + release |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen | C0 | 40 | 47 | 0 | 8 | 39 | 39 | 0 | 50: 40 + 10 |
| qwen | C1 | 24 | 63 | 18 | 9 | 36 | 36 | 0 | 35: 24 + 11 |
| kimi | C0 | 24 | 63 | 0 | 2 | 61 | 58 | 3 | 29: 24 + 5 |
| kimi | C1 | 18 | 69 | 18 | 5 | 46 | 43 | 3 | 20: 18 + 2 |

For every row: first T* fail = P0-public-stop/T*-fail + R1-public-stop/T*-fail + prepared R2. Prepared R2 = actual R2 + local admission refusal. Final T* pass = retained public-stop success + success after a release generation. Qwen C0 therefore has 47 first T* failures but only 39 releases: eight first deliveries already pass C0 and stop while failing T*. C1 adds 18 P0 early-stopped observations (six tasks × three repetitions), all T*-failing.

Strict and normalized C0 branches share these exact counts, delivery outcomes, and logical costs. They are one row here, not additive spending. Refusal means no API generation was sent; it is not a decoder rejection. All local refusals occur on task 989, for three repetitions in both pools and both opportunities. No unsent global-stop positions or selected-task UNKNOWN outcomes remain.

## Partition outcomes by baseline stopping stratum

The six-task stratum is fixed by C1 P0 public passage, before any repair generation: 595, 713, 796, 860, 1097, 1111. The remaining 23 tasks have repair-feedback trajectories under both public pools. All 29 were selected conditional on C0 failure. These are descriptive strata, not randomized populations or forced-generation counterfactuals.

| Service | Stratum (tasks) | Phase | C1 / C0 successes | Both / C1 only / C0 only / neither | Discordant tasks | C1 − C0 pp |
| --- | --- | --- | --- | --- | --- | --- |
| qwen | C1_P0_early_stop (6) | first | 0 / 9 | 0 / 0 / 9 / 9 | 3 | -50.00 |
| qwen | C1_P0_early_stop (6) | final | 0 / 13 | 0 / 0 / 13 / 5 | 5 | -72.22 |
| qwen | repair_feedback (23) | first | 24 / 31 | 24 / 0 / 7 / 38 | 3 | -10.14 |
| qwen | repair_feedback (23) | final | 35 / 37 | 33 / 2 / 4 / 30 | 3 | -2.90 |
| kimi | C1_P0_early_stop (6) | first | 0 / 6 | 0 / 0 / 6 / 12 | 4 | -33.33 |
| kimi | C1_P0_early_stop (6) | final | 0 / 10 | 0 / 0 / 10 / 8 | 5 | -55.56 |
| kimi | repair_feedback (23) | first | 18 / 18 | 13 / 5 / 5 / 46 | 9 | 0.00 |
| kimi | repair_feedback (23) | final | 20 / 19 | 15 / 5 / 4 / 45 | 8 | 1.45 |

## Logical generation costs by stratum

| Service | Stratum (tasks) | Pool | R1 gen | R2 prepared / actual | R1 tokens | R2 tokens | Total tokens | Generation HTTP s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen | C1_P0_early_stop (6) | C0 | 18 | 9 / 9 | 90081 | 45055 | 135136 | 135.732 |
| qwen | repair_feedback (23) | C0 | 69 | 30 / 30 | 357440 | 147811 | 505251 | 490.220 |
| qwen | C1_P0_early_stop (6) | C1 | 0 | 0 / 0 | 0 | 0 | 0 | 0.000 |
| qwen | repair_feedback (23) | C1 | 69 | 36 / 36 | 352689 | 176817 | 529506 | 520.005 |
| kimi | C1_P0_early_stop (6) | C0 | 18 | 12 / 12 | 80930 | 55067 | 135997 | 93.781 |
| kimi | repair_feedback (23) | C0 | 66 | 49 / 46 | 296526 | 218064 | 514590 | 323.607 |
| kimi | C1_P0_early_stop (6) | C1 | 0 | 0 / 0 | 0 | 0 | 0 | 0.000 |
| kimi | repair_feedback (23) | C1 | 66 | 46 / 43 | 293573 | 198527 | 492100 | 304.892 |

Tokens are provider-reported generation usage, not dollars; execution costs remain in the complete study accounting. HTTP seconds are observed acquisition components, not end-to-end or pure inference latency. C0-normalized is reused by interface and partition comparisons, and strict C0 is shared, so these rows must not be summed across experiments/policies to reconstruct physical spending.

## Task-weighted paired cost differences

| Service | Stratum | Phase | C0 tokens | C1 tokens | C1 − C0 tokens per task–repeat |
| --- | --- | --- | --- | --- | --- |
| qwen | C1_P0_early_stop | first | 90081 | 0 | -5004.50 |
| qwen | C1_P0_early_stop | final | 135136 | 0 | -7507.56 |
| qwen | repair_feedback | first | 357440 | 352689 | -68.86 |
| qwen | repair_feedback | final | 505251 | 529506 | 351.52 |
| kimi | C1_P0_early_stop | first | 80930 | 0 | -4496.11 |
| kimi | C1_P0_early_stop | final | 135997 | 0 | -7555.39 |
| kimi | repair_feedback | first | 296526 | 293573 | -42.80 |
| kimi | repair_feedback | final | 514590 | 492100 | -325.94 |

All arithmetic identities and stratum-to-total sums are asserted by reconstruct.py. Repetitions remain nested within tasks; no p-values, equivalence tests, or population confidence intervals are manufactured.
