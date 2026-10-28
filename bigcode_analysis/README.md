# BigCodeBench analysis replay

This local, unpublished subset reproduces the arithmetic in Tables 13, 15, 17 and G1–G2 of the manuscript from a safe projection of the closed analysis. It does not rerun models, candidates, tests, or the original analysis pipeline. It does not independently validate the underlying execution records.

## Run

With Python 3.8 or later, from this directory:

```console
python replay.py
```

This prints the five tables without changing any files. The included `replay_report.md` records one successful replay. For a fresh copy without that report, `python replay.py --write-report` creates it exclusively and refuses to overwrite an existing report. Only the Python standard library is used; no network access or package installation is required.

## Contents and provenance

- `safe_projection.json`: 522 logical branch rows covering 29 tasks, two services, three repetitions, and three policies; initial public/complete outcomes, four physical acquisition ledgers, execution-stage totals, and the original aggregate values used for arithmetic cross-checks.
- `replay.py`: verifies the fixed input digest and population, recomputes task-paired effects and costs, and checks them against the projected aggregate values.
- `replay_report.md`: the single recorded arithmetic replay.
- `README.md`: scope and interpretation.

Source safe-analysis SHA-256: `0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650`.

Projection SHA-256: `902ab00dddaac937b841e0c4b4c97759d377d1077ae817c3bbf4f212e3cf741c`.

The projection omits responses, program source, tests and test-method names, service configuration, credentials, absolute paths, and raw execution logs. It cannot reproduce generation or test execution. Its input digest is fixed in the replay script. Aggregate cross-checks detect arithmetic inconsistencies; they are not an independent replication from raw evidence.

## Interpretation

The active three-domain population A is empty. The online-interface comparison B and public-partition comparison C use the same 29 tasks. Three repetitions are nested within each task, and services are reported separately. The 87 task–repetition observations per service are not 87 independent tasks. First and final outcomes refer to bank deliveries on the shared complete test set T*, not merely to public-test passage or acceptance of a raw response.

`C0_normalized` and `C0_strict` share the same physical first responses and, in this run, the same subsequent trajectories. Their logical cost rows must not be added. Experiment C also reuses the C0-normalized branch from experiment B. Physical acquisition totals count each request once; local input-budget refusals are unsent positions, not generation calls. Tokens per final passing delivery include spending on unsuccessful trajectories and exclude separately reported execution expenses. Provider token units are not a common monetary unit.

Table 15 averages each task's three paired outcome differences, then weights tasks equally. Table G1 shows net success-count differences across those three repetitions. C1 initial all-pass tasks remain in the denominator and retain P0 through early stopping. No confidence interval, population-level equivalence claim, or causal model-internals explanation is inferred. Reported HTTP and execution-stage times are accounting components, not total research time or pure inference latency.

## Release status and rights

This directory is a local review artifact and has no public release URL. No project or third-party license is assigned by this package. Authors must approve rights, attribution, anonymity, and the publication platform before an external release. The older replay package is unchanged.

The manuscript transition revision adds Tables 14, 16 and G3, reproduced by the separate `bigcode_transition_audit_20261026` subset. External release is deferred at the author's request until a repository is specified.
