# Prospective two-task repeated scope results

The 40-algorithm intake yielded two tasks with different executable SEED/FULL permissions. These two tasks are the independent task denominator; three repetitions per service do not create six independent tasks.

## Task-level repeated outcomes

| Service | Delivery | Task | Policy | PASS / repetitions | UNKNOWN | Task mean |
|---|---|---|---|---:|---:|---:|
| qwen | first_opportunity | quixbugs:next_palindrome | SEED | 0/3 | 0 | 0.0 |
| qwen | first_opportunity | quixbugs:next_palindrome | CLOSURE | 0/3 | 0 | 0.0 |
| qwen | first_opportunity | quixbugs:next_palindrome | FULL | 0/3 | 0 | 0.0 |
| qwen | first_opportunity | quixbugs:pascal | SEED | 0/3 | 0 | 0.0 |
| qwen | first_opportunity | quixbugs:pascal | CLOSURE | 3/3 | 0 | 1.0 |
| qwen | first_opportunity | quixbugs:pascal | FULL | 3/3 | 0 | 1.0 |
| qwen | final_delivery | quixbugs:next_palindrome | SEED | 0/3 | 0 | 0.0 |
| qwen | final_delivery | quixbugs:next_palindrome | CLOSURE | 0/3 | 0 | 0.0 |
| qwen | final_delivery | quixbugs:next_palindrome | FULL | 0/3 | 0 | 0.0 |
| qwen | final_delivery | quixbugs:pascal | SEED | 3/3 | 0 | 1.0 |
| qwen | final_delivery | quixbugs:pascal | CLOSURE | 3/3 | 0 | 1.0 |
| qwen | final_delivery | quixbugs:pascal | FULL | 3/3 | 0 | 1.0 |
| kimi | first_opportunity | quixbugs:next_palindrome | SEED | 3/3 | 0 | 1.0 |
| kimi | first_opportunity | quixbugs:next_palindrome | CLOSURE | 3/3 | 0 | 1.0 |
| kimi | first_opportunity | quixbugs:next_palindrome | FULL | 3/3 | 0 | 1.0 |
| kimi | first_opportunity | quixbugs:pascal | SEED | 0/3 | 0 | 0.0 |
| kimi | first_opportunity | quixbugs:pascal | CLOSURE | 3/3 | 0 | 1.0 |
| kimi | first_opportunity | quixbugs:pascal | FULL | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:next_palindrome | SEED | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:next_palindrome | CLOSURE | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:next_palindrome | FULL | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:pascal | SEED | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:pascal | CLOSURE | 3/3 | 0 | 1.0 |
| kimi | final_delivery | quixbugs:pascal | FULL | 3/3 | 0 | 1.0 |

## Within-service SEED minus FULL

| Service | Delivery | Tasks | Mean of task means | SEED wins | FULL wins | Ties | Unknown pairs |
|---|---|---:|---:|---:|---:|---:|---:|
| qwen | first_opportunity | 2 | -0.5 | 0 | 3 | 3 | 0 |
| qwen | final_delivery | 2 | 0.0 | 0 | 0 | 6 | 0 |
| kimi | first_opportunity | 2 | -0.5 | 0 | 3 | 3 | 0 |
| kimi | final_delivery | 2 | 0.0 | 0 | 0 | 6 | 0 |

The first-opportunity bank is primary; final two-opportunity delivery is secondary. The six paired repetition counts per service are descriptive, not six independent task observations.

CLOSURE equals SEED for next_palindrome and FULL for pascal. No task has a selective intermediate closure, and this panel cannot isolate an incremental closure-expansion effect.

The original 32 historical aggregate rows remain in core_results.*. They are not pooled with this panel. All 24 first/final task-repetition pairs, 72 delivery aliases and two P0 outcomes are retained in the separate CSV tables.

Model-cost CSV rows distinguish physical calls from overlapping logical arm costs. Do not sum logical rows or compare raw token ratios between service tokenizers. Public execution, held-out execution and prior preparation have separate rows. Costs are copied from the closed accounting summary; this replay does not reconstruct per-request accounting from raw ledgers.

Strict/normalized response acceptance is an interface diagnostic within the actual normalized trajectories. No alternative strict trajectory is reconstructed. No significance, equivalence or population superiority claim follows from two tasks.
