# Closed BigCodeBench transition audit

This local, unpublished five-file subset reconstructs the first-opportunity-to-release transitions and the baseline-stopping strata of the completed BigCodeBench experiment. It uses only safe metadata projected from the closed analysis. It performs no model requests, program execution, test execution, network access, or hidden-source access, and does not rerun the original analysis pipeline.

## Run

With Python 3.8 or later and no additional packages:

```console
python reconstruct.py
```

The script validates the fixed projection digest, checks all branch populations and arithmetic identities, and prints the transition and stratum tables without writing files. `python reconstruct.py --write` is available only on a fresh copy without `transition_summary.json` and `tables.md`; it refuses to overwrite either output. The included outputs were created once. A Windows console-encoding error occurred only while printing after their successful creation; stdout is now explicitly UTF-8. A subsequent read-only replay printed the same computed tables successfully.

## Files

- `safe_projection.json`: 522 safe logical branch rows, initial public/complete outcome labels, logical cost/status counters, and provenance hashes. It includes no source code, tests, method names, raw requests/responses, service configuration, credentials, or absolute paths.
- `reconstruct.py`: standard-library arithmetic reconstruction with assertions.
- `transition_summary.json`: machine-readable transition counts, two-stratum summaries, and task-level paired outcome/token details.
- `tables.md`: readable tables and interpretation.
- `README.md`: this document.

Projection SHA-256: `4502552cd74dd873252f4c9711dbe7fd402d3623559e8b48e3701723c95aae61`.

Closed source analysis SHA-256: `0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650`.

Prior safe projection SHA-256: `902ab00dddaac937b841e0c4b4c97759d377d1077ae817c3bbf4f212e3cf741c`.

## What is reconstructed

The report uses semantic table names to allow manuscript renumbering. JSON `transitions` has four rows, one per service and public pool; strict C0 and normalized C0 are verified identical in all projected branch fields except policy name, then displayed once. `stratum_transitions` has eight rows (two services × two pools × two strata). `stratum_pairs` has eight rows (two services × two timepoints × two strata), including task-level paired details.

The six-task stratum is defined by initial C1 public passage: tasks 595, 713, 796, 860, 1097, and 1111. Its 18 task–repetition observations stop before generation under C1, while C0 proceeds. The other 23 tasks are the repair-feedback stratum. This classification precedes repair generation and is not chosen from repair success. All 29 tasks were selected conditional on C0 failure; strata describe this conditional intake and are not a randomized comparison of test partitions.

First and final T* outcomes are outcomes of the delivered bank program, not just the raw response. Public-bank passage determines stopping; T* was evaluated only after global sealing. Therefore a T*-failing first delivery can legitimately have no continuation because its public checks pass. Local admission refusal denotes an unsent model position, distinct from a captured reply rejected by the decoder. All such local refusals are on task 989. No selected-task UNKNOWN outcome or unsent global-stop position is present.

Three repetitions remain within each independent task. Cost differences average those three paired differences within task, then weight tasks equally. Tokens are provider-reported usage, not comparable monetary units across services. HTTP seconds are acquisition components, not pure inference or end-to-end latency. C0 policies and experiment labels share requests; logical columns must not be added to reconstruct physical spending. Complete execution costs are retained in the parent study's accounting.

This replay checks arithmetic consistency of a safe projection. It does not independently revalidate model behavior, source-level acceptance, or test execution. It supports manuscript Tables 14, 16 and G3. There is no public release URL or license grant in this directory. The author deferred external publication on 26 October 2026 until a repository is specified. The prior replay subset's data are unchanged; only its displayed table references were synchronized with manuscript renumbering.
