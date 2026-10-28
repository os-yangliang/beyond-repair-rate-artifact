# Task-paired intervals for the closed BigCodeBench panel

This package computes a **post-hoc secondary analysis** of already public, sanitized metadata. Outcomes were known before the analysis plan was written. The plan was fixed before interval computation, but this is **not a preregistered experiment or confirmatory analysis**. There are no new model requests, candidate executions, tests, network requests, or accesses to held-out test contents.

## What is compared

Every difference is **C1-normalized minus C0-normalized**. For each task and service, the three paired repetition differences are averaged first. A task, with its service/stage/cost measurements kept together, is the resampling unit. Three repetitions do not become three independent tasks.

The 29-task cohort was originally selected for initial C0 failure. Six of those initial programs already passed C1 and therefore stopped under C1 without generation. The **23-task repair-feedback stratum**, defined from initial public outcomes before generation, is the primary stratum for comparing repair trajectories. The full 29-task result is also retained because early stopping is part of the workflow. The six-task early-stop stratum is reported descriptively, without intervals. Local-refusal task 989 remains in every applicable denominator.

T* denotes the already recorded complete evaluation outcome. A first-stage outcome is not the same estimand as final delivery after an available release opportunity. All costs are logical trajectory costs; shared physical requests must not be obtained by summing logical arms.

## Results

Pointwise 95% task-bootstrap percentile intervals are in brackets. Tokens are the mean total tokens per task/repetition trajectory, not a corpus-total difference. A negative cost difference means C1 used fewer logical tokens.

| Service | Cohort | First T* difference (pp) | Final T* difference (pp) | Total-token mean difference |
|---|---|---:|---:|---:|
| Qwen | All selected, 29 tasks | -18.39 [-33.33, -5.75] | -17.24 [-33.33, -3.45] | -1,274.49 [-2,602.93, -94.02] |
| Qwen | Repair feedback, 23 tasks | -10.14 [-23.19, 0.00] | -2.90 [-14.49, 7.25] | 351.52 [-69.48, 902.81] |
| Kimi | All selected, 29 tasks | -6.90 [-18.39, 3.45] | -10.34 [-24.14, 2.30] | -1,821.69 [-3,047.76, -692.64] |
| Kimi | Repair feedback, 23 tasks | 0.00 [-10.14, 10.14] | 1.45 [-7.25, 11.59] | -325.94 [-975.19, 269.81] |

All primary repair-feedback intervals include or touch zero. This is neither evidence of equivalence nor proof that an effect is absent. The full-cohort token reduction includes six C1 early stops, so it cannot be interpreted as a cost advantage of repair feedback alone. Full-cohort intervals also inherit the original C0-failure selection.

The full output additionally reports prepared-continuation and actual-second-generation rate differences, first-round tokens, and generation/tokenizer HTTP-duration components. Kimi tokenizer duration is zero in the source metadata for both arms; its four stratum/metric intervals are mechanically [0, 0], not evidence of identical end-to-end speed. HTTP durations are recorded request components, not total elapsed workflow latency or pure inference time. Token units are provider-specific and are not dollar costs.

## Reproduce without an experiment

Use Python 3.9 or newer; only the standard library is required. Run from this directory:

```text
python analyze.py --out reproduced_results
```

The destination must not already exist. The default destination is `results`, which is included and therefore protected from accidental overwrite. The script checks the input and plan hashes before calculating anything, calculates all results and validates them, and then writes the output directory. It does not import or execute any benchmark program.

The fixed algorithm uses `random.Random(20261028)`, 20,000 resamples per stratum, and one RNG stream in the order all 29 tasks then the 23-task stratum. Tasks are sorted numerically. Each draw uses `random.choices(range(n), k=n)`. One draw is shared across services and all metrics within its stratum, retaining their paired relationships. Each stratum is resampled within its own task population. The 2.5th and 97.5th percentiles use type-7 linear interpolation, with index `(B - 1) * p`. Bootstrap index-stream hashes are saved to identify the exact draws.

Validation has three components:

1. Exact source identity, all 522 logical rows, all 29 task identities, all design cells, known endpoint and usage values, identical shared C0 receiver rows, and retained local refusals.
2. Eighteen primary point estimates checked against the closed analysis's aggregate counts/token totals, plus twenty checks that the 6/23-task weighted decomposition reconstructs the 29-task mean.
3. Forty quantile/moment checks: a separately implemented standard-library inclusive quantile agrees with each type-7 interval; Monte Carlo means and variances agree with the exact empirical-bootstrap moments of a task mean. The four zero-variance metrics are kept explicitly.

## Interpretation and limits

These are exploratory, pointwise task-resampling intervals conditional on the selected tasks, policies, recorded responses, and three collected repetitions. They are not simultaneous or multiplicity-adjusted intervals. No hypothesis test, policy-ranking claim, or equivalence test is performed.

The finite cohort's observed means are already known. Resampling does not create uncertainty about those recorded means; it describes variability under an empirical task-resampling model. Exchangeability is an approximation, and related task families may violate independence. The intervals do not correct cohort selection, establish representativeness of all software defects, or capture new within-task generation variability or rolling-service drift. The separate all-task and repair-feedback intervals are not two independent studies. No population interval is calculated for the two QuixBugs cases.

## Files and provenance

- `analysis_plan.json` and `analysis_plan.md`: choices recorded before computing these intervals; expressly retrospective.
- `safe_projection.json`: exact copy of the previously published sanitized transition-audit input. It contains task identifiers, outcomes, counts, durations, and hashes, not test bodies, prompts, raw responses, code, or credentials.
- `analyze.py`: complete standard-library analysis and validation.
- `results/task_differences.csv`: 58 task/service rows after paired repetition averaging.
- `results/interval_results.json` and `.csv`: 40 service/stratum/metric intervals and provenance.
- `results/early_stop_descriptive.csv`: six-task-stratum aggregate descriptions; no intervals.
- `results/main_table.md`: four-row manuscript table.
- `results/validation.json`: point-estimate, decomposition, quantile, and bootstrap-moment checks.
- `manifest.json`: relative filenames, sizes, and SHA-256 hashes; excludes itself.

Input SHA-256: `4502552cd74dd873252f4c9711dbe7fd402d3623559e8b48e3701723c95aae61`.

Plan SHA-256: `1e32a8814f34db9f8ceb347c9ea5007793ec17d26e9f907baf69907a73a2485a`.

Source-analysis SHA-256: `0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650`.

This directory prepares a publication subset. Creating these files does not itself publish them or supply an external archive URL.
