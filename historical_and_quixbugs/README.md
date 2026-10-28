# UMA-CRA article: portable analysis replay v2

This local package reconstructs outcome tables from sanitized metadata. It is
**analysis reproduction**, not model rerunning or program/test execution. It
requires Python 3.9 or newer and the standard library only. It makes no network
requests and needs no credentials, original workspace, model, Docker or benchmark
installation.

## Run

Copy the complete package to any directory and run:

```text
python replay.py
```

The default inputs and outputs are relative to the script. To create another
table copy, use `python replay.py --out rebuilt_tables`. The script replaces only
its generated table files, never inputs or experimental records.

## Historical results and prospective repetitions remain separate

`inputs/history/` contains the same six safe projections as v1, with their
original bytes and hashes. The fixed historical replay code regenerates the
original **32 aggregate rows** in `tables/core_results.*`, plus historical
identity and paired tables. It does not re-read or distribute the six original
analysis files.

`inputs/prospective.json` adds the QuixBugs panel separately: 72 first/final
delivery aliases and two original-program outcomes. The natural intake contained
40 algorithms; two tasks met the frozen executable SEED/FULL contrast condition.
Each service has three repetitions per task. The independent task denominator is
**two**, not six, 12, 72, or the original 40 algorithms.

The added tables are:

- `prospective_identity_outcomes.csv` and `prospective_P0_outcomes.csv`: every
  projected delivery and original-program outcome, including failures/UNKNOWN;
- `prospective_task_means.csv`: each task's successes over three repetitions;
- `prospective_paired_repetitions.csv`: all within-service SEED/FULL paired
  repetitions, with CLOSURE outcomes retained;
- `prospective_paired_task_means.csv`: each service's mean of the two task-level
  paired effects, separately for first-opportunity and final deliveries;
- `prospective_model_costs.csv`, `prospective_execution_costs.csv`, and
  `prospective_response_acceptance.csv`: allowlisted numeric accounting and
  strict/normalized decoder diagnostics;
- `prospective_results.json` and `.md`: the new tables and interpretation;
- `prospective_input_hashes.json`: provenance for the additional input.

The first-opportunity bank is the primary outcome; final delivery follows the
actual own-history two-opportunity policy. Qwen uses the frozen per-task,
per-repetition seeds; Kimi repetitions are separate requests without a claimed
deterministic seed. CLOSURE equals SEED for `next_palindrome` and FULL for `pascal`.
There is no selective intermediate-closure contrast. This panel cannot establish
a separate closure-expansion benefit.

Within each task/service/repetition/opportunity, identical requests may share a
physical response. Model responses are never reused across repetitions.
Logical-arm costs overlap and must not be summed as physical cost. Token counts
use each service's tokenizer; no cross-service token-efficiency ratio is inferred.
Model, new public execution, held-out execution, original public observation and
interface validation costs are separate. The cost tables reproduce closed
summary accounting; they do not independently rebuild per-request ledgers.

Strict decoder acceptance is a paired diagnostic on the same replies. The
actual prospective policy uniformly removes only complete leading ASCII blank
lines before the original decoder. These diagnostics do not construct a second
strict-policy repair history or estimate saved calls.

## Included information and limits

Inputs contain only task/policy/service/repetition/timepoint identifiers,
public and endpoint outcomes, safe domain strata, numeric costs, and originating
analysis hashes/byte counts. They do not contain candidate source, prompts,
responses, test code or values, reference solutions, credentials, server addresses,
absolute paths, or the original analyses' source-pin inventories. The original
analyses themselves are not bundled.

The replay verifies bundled-input hashes and recalculates outcomes and task means
from individual rows. Originating hashes document provenance but require the
separately retained original analyses for independent verification. Integrity
hashes are not proof of experimental correctness.

PASS refers only to the committed examples. UNKNOWN remains distinct from FAIL
and is not silently omitted. No significance test, bootstrap interval, population
equivalence, or general superiority claim is produced. Historical studies and
the prospective panel are not pooled. The historical first-response format
diagnostic remains a fixed-response analysis, not a new two-round trajectory.

This package does not recreate figures, source-level case analyses, raw service
ledgers, benchmark acquisition, or the full experimental pipeline. It has no
public hosting URL. A hosting destination, license and complete artifact release
are separate publication tasks; a local package is not an external publication.
