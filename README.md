# Beyond Repair Rate — analysis artifact

This artifact accompanies **Beyond Repair Rate: Auditing Effective Edit Permissions and Response Acceptance in LLM-Based Program Repair**, the standalone manuscript prepared in October 2026. It provides sanitized outcome metadata and offline arithmetic reproduction. It does **not** rerun a model, execute a candidate or a test, or independently reconstruct the original experimental records.

The package combines three closed analysis subsets without changing their bytes: 38 copied files plus root-level assembly documentation, manifest and runner. Statements such as “local, unpublished”, “publication deferred”, and old table numbers in the copied subsets are **dated provenance from their preparation**, not the current repository's publication status or the current manuscript's numbering. The current mapping is below.

## One-command offline reproduction

Requirements: Python **3.9 or later**, standard library only. No package installation, network connection, credentials, model, Docker or benchmark installation is required. From the repository root:

```console
python reproduce.py
```

The runner verifies every copied file against `manifest.json`, invokes the three existing entry points, rebuilds the historical/QuixBugs tables, and compares regenerated outputs with the archived outputs. Logs, rebuilt tables and `verification.json` go into a new `reproduced/` directory. An existing output directory is refused; select a new destination for another run:

```console
python reproduce.py --out another_reproduction
```

Exit code 0 and `"status": "passed"` mean the bundled arithmetic and output comparisons succeeded. A failed run returns a nonzero code and preserves logs and its failure report. Frozen inputs are not rewritten. CSV comparisons use parsed cells, JSON comparisons use parsed values, and Markdown comparison normalizes line endings only. This avoids treating operating-system line endings as a changed result. The transition entry point prints an already newline-terminated report; its one extra console-print newline is removed before comparison.

Component commands remain available:

```console
python historical_and_quixbugs/replay.py --out another_historical_table_copy
python bigcode_analysis/replay.py
python bigcode_transitions/reconstruct.py
```

The last two commands print reports without changing copied files. The root runner suppresses Python bytecode-cache creation.

## Contents

| Directory | Frozen files | Reproduction scope |
|---|---:|---|
| `historical_and_quixbugs/` | 29 | Six historical outcome projections, their 32 aggregate rows and identity/paired tables; separate two-task QuixBugs repeated outcomes, task means and numeric cost/acceptance summaries. |
| `bigcode_analysis/` | 4 | Arithmetic over 522 logical branches for the same 29 BigCodeBench tasks, two services and three task-nested repetitions; complete outcomes, paired effects, physical acquisition and execution-stage summaries. |
| `bigcode_transitions/` | 5 | First-opportunity and release transitions, local refusals, six-task early-stop and 23-task repair-feedback strata, and task-paired outcomes/costs. |

BigCodeBench's two subsets overlap in observations and are not independent studies. Logical branches can share physical requests. QuixBugs has two independent tasks, not six per service; repetitions remain within tasks. Refactory windows remain separate and share five assignment families. UNKNOWN remains separate. No significance test, equivalence finding or general policy ranking is generated.

## Mapping to the current standalone manuscript

The runner reconstructs the **bundled analysis outputs**, not a typeset copy of every manuscript table. Paths beginning `tables/` below are relative to `historical_and_quixbugs/`.

| Current manuscript item | Available reconstruction | Material not reproduced here |
|---|---|---|
| **Table 1 — coverage funnel** | `inputs/prospective.json` and `tables/prospective_results.json` retain QuixBugs population counts; projected identity/domain labels retain selected repair strata. `bigcode_analysis/safe_projection.json` records the empty active-domain and 29-task outcome cohorts. | The complete intake-to-active funnel, source-level domain classification and all exclusion decisions are absent. This is not full Table 1 reproduction. |
| **Table 2 — initial/final outcomes and logical cost** | `tables/core_results.*`: Refactory final and HumanEvalPack original first/final complete outcomes. `tables/prospective_task_means.csv` and `tables/prospective_model_costs.csv`: QuixBugs repeated outcomes and aggregate logical generation counts/tokens. | Refactory public-only first outcomes and full historical continuation/token accounts are absent. The complete table is not regenerated. |
| **Table 3 — 52-response admission transitions** | `tables/core_results.*` and `tables/identity_outcomes.csv` retain the separate original/normalized **fixed-first-response outcome** projection discussed alongside this table. | The 52 physical-response admission records are absent: A-to-A/R-to-A counts and source-byte/AST equality checks cannot be recomputed. Logical outcome aliases are not physical responses. |
| **Table 4 — BigCodeBench transition and cost account** | `bigcode_transitions/transition_summary.json` (`transitions`) and `tables.md`: four service/partition columns, stopping/refusal/release identities and logical costs. Tokens per final pass = total tokens / final passes. `bigcode_analysis/replay_report.md` cross-checks complete outcomes and costs. | Raw request and execution ledgers are absent; reproduction is arithmetic over projected metadata. |
| **Table 5 — BigCodeBench baseline strata** | `bigcode_transitions/transition_summary.json` (`stratum_pairs`, `stratum_transitions`) and `tables.md`: six/23-task strata, first/final outcomes, tokens and task-weighted paired token differences. | No forced-generation counterfactual for initially C1-passing tasks is reconstructed. |
| **Table 6 — exact paired outcomes** | `tables/identity_outcomes.csv`: historical final pairs and the four-task executable HumanEvalPack subset. `tables/prospective_paired_repetitions.csv`: QuixBugs pairs. BigCodeBench overall pairs: `bigcode_analysis/replay_report.md`; stratum pairs: `bigcode_transitions/transition_summary.json`. | Refactory public-only first pairs are absent. Historical `paired_outcomes.csv` groups equal known outcomes; identity rows distinguish both-success from neither-success. No full Table 6 renderer is supplied. |
| **Table 7 — physical acquisition** | `tables/prospective_model_costs.csv`: QuixBugs physical generation/tokenizer counts and tokens. `bigcode_analysis/replay_report.md` and its projection: BigCodeBench counts, tokens, HTTP components and collection time. | Historical acquisition and QuixBugs HTTP/collection times are absent. Execution summaries are separate and are not end-to-end latency. Full Table 7 is not reproduced. |
| **Table A1 — executable HumanEvalPack cases** | Filter `tables/identity_outcomes.csv` to the original HumanEvalPack services and Python/5, Python/43, Python/48 and Python/52 to recover first/final policy outcomes. | Task-level token differences are absent. |
| **Table A2 — QuixBugs task-cost means and SDs** | `tables/prospective_task_means.csv` provides repeated task **outcome** means; `tables/prospective_model_costs.csv` provides aggregate arm costs. | Per-task/per-repetition costs required for these cost means and sample SDs are absent. Table A2 is not reproduced by aggregate cost rows. |

Old report headings “Tables 13/15/17/G1/G2” and “Tables 14/16/G3” refer to the longer historical draft. They remain untouched for provenance, not as additional standalone-manuscript tables.

## Integrity and evidence limits

`manifest.json` lists the path, size and SHA-256 of all 38 copied files. Their original manifests and input-hash checks remain intact. BigCodeBench analysis and transition projection hashes respectively are:

- `902ab00dddaac937b841e0c4b4c97759d377d1077ae817c3bbf4f212e3cf741c`
- `4502552cd74dd873252f4c9711dbe7fd402d3623559e8b48e3701723c95aae61`

Both identify the closed source-analysis hash `0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650`. Hashes document integrity/provenance; they are not proof of experimental correctness. Original analyses are not bundled.

No raw model reply or prompt, candidate/reference program, test source or expected value, model weight, Docker image, service configuration or credential is included. Task IDs, outcome labels, numeric accounting and hashes are retained. This artifact does not reproduce figures, source-level audits, sampling, raw-code acceptance validation, candidate execution or held-out evaluation. Fixed-response diagnosis cannot construct an unobserved online history.

Tokens remain service-specific, and overlapping logical rows must not be summed as physical spending. Equal final results after release are not evidence of equivalent first-attempt permissions. See `LICENSE_STATUS.md` for rights information supplied with this publication.
