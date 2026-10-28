# BigCodeBench safe-summary arithmetic replay

Local, unpublished metadata subset. A = 0; B and C use the same 29 tasks.
Three repetitions are nested within task. Services remain separate. No model or test was rerun.
Input SHA-256: `902ab00dddaac937b841e0c4b4c97759d377d1077ae817c3bbf4f212e3cf741c`.
Source safe-analysis SHA-256: `0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650`.

## Table 13: complete T* delivery and logical continuation cost

| Service | Policy | First / 87 | Final / 87 | Actual / prepared release | Total tokens | Tokens / final pass |
| --- | --- | --- | --- | --- | --- | --- |
| qwen | C0 strict = normalized | 40 | 50 | 39 / 39 | 640,387 | 12,807.7 |
| qwen | C1 normalized | 24 | 35 | 36 / 36 | 529,506 | 15,128.7 |
| kimi | C0 strict = normalized | 24 | 29 | 58 / 61 | 650,587 | 22,434.0 |
| kimi | C1 normalized | 18 | 20 | 43 / 46 | 492,100 | 24,605.0 |

Tokens include unsuccessful trajectories. Logical policy rows overlap; do not sum them as physical spending.

## Table 15: C1-minus-C0 paired complete outcomes

| Service | Delivery | Task mean difference (pp) | Both / C1 only / C0 only / neither | Discordant tasks |
| --- | --- | --- | --- | --- |
| qwen | first | -18.39 | 24 / 0 / 16 / 47 | 6 / 29 |
| qwen | final | -17.24 | 33 / 2 / 17 / 35 | 8 / 29 |
| kimi | first | -6.90 | 13 / 5 / 11 / 58 | 13 / 29 |
| kimi | final | -10.34 | 15 / 5 / 14 / 53 | 13 / 29 |

Effects average three paired repetitions within each task, then weight tasks equally. No confidence interval or equivalence claim is computed.

## Table 17: actual physical acquisition

| Service | Generations | Tokenizer | Local unsent | Reported tokens | Generation HTTP (s) | Tokenizer HTTP (s) |
| --- | --- | --- | --- | --- | --- | --- |
| qwen | 231 | 231 | 0 | 1,169,893 | 1,145.957 | 44.590 |
| kimi | 251 | 0 | 12 | 1,142,687 | 722.280 | 0.000 |

Total reported generation tokens: 2,312,580; unknown usage: 0.
Collection-stage wall time: 2,049.281 s. HTTP components are not pure inference or end-to-end latency; provider token units are not a common currency.

## Table G1: task-level differences across three repetitions

| Task | Qwen first | Qwen final | Kimi first | Kimi final |
| --- | --- | --- | --- | --- |
| 595 * | 0 | -1 | 0 | 0 |
| 713 * | -3 | -3 | -1 | -1 |
| 722 | 0 | -1 | -1 | -1 |
| 765 | 0 | +2 | 0 | 0 |
| 796 * | -3 | -3 | 0 | -2 |
| 860 * | 0 | -3 | -1 | -1 |
| 898 | -1 | 0 | -1 | -1 |
| 912 | -3 | 0 | +1 | +1 |
| 956 | 0 | 0 | -1 | -1 |
| 958 | 0 | 0 | +1 | +1 |
| 989 | -3 | -3 | 0 | 0 |
| 1009 | 0 | 0 | +2 | +2 |
| 1097 * | -3 | -3 | -3 | -3 |
| 1108 | 0 | 0 | -1 | -1 |
| 1110 | 0 | 0 | -1 | 0 |
| 1111 * | 0 | 0 | -1 | -3 |
| 1112 | 0 | 0 | +1 | +1 |

* C1 initial all-pass and P0 early stopping. Unlisted tasks have no paired outcome discordance.
- qwen first: six early-stop tasks contribute -9; other 23 contribute -7.
- qwen final: six early-stop tasks contribute -13; other 23 contribute -2.
- kimi first: six early-stop tasks contribute -6; other 23 contribute +0.
- kimi final: six early-stop tasks contribute -10; other 23 contribute +1.

## Table G2: full physical execution account

| Component | Jobs | CLI | Stage seconds |
| --- | --- | --- | --- |
| integration | 18 | 162 | 42.435 |
| initial_C0 | 1,173 | 10,557 | 2,571.523 |
| C1_P0 | 207 | 1,863 | 438.567 |
| candidate_public | 741 | 6,669 | 1,563.661 |
| endpoint | 441 | 3,969 | 929.090 |
| Total | 2,580 | 23,220 | 5,545.277 |

Endpoint reused 339 public vectors with zero new jobs for those observations.
The initial resource failure and all controls remain included. Stage seconds are summed accounting components, not end-to-end research latency.

## Scope

All displayed arithmetic agrees with the projected safe-analysis summaries. This does not independently authenticate raw requests, source code, test execution, the scientific oracle or model behavior. The subset has not been publicly released; no project or third-party license is assigned here.
