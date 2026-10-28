"""Portable standard-library replay of historical and two-task repeated outcomes.

Only sanitized JSON metadata is read. No model, candidate, or test is executed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

import historical_replay as history

HERE = Path(__file__).resolve().parent
HISTORY_CODE_SHA = "ab7822ed4ceca5c9a77f27bd7c60cc0750a194d19413cd88fe76e726de79fad0"
TASKS = ("quixbugs:next_palindrome", "quixbugs:pascal")
SERVICES, ARMS, REPS = ("qwen", "kimi"), ("SEED", "CLOSURE", "FULL"), (0, 1, 2)
POINTS = ("first_opportunity", "final_delivery")
STRATA = {TASKS[0]: "SEED = CLOSURE < FULL", TASKS[1]: "SEED < CLOSURE = FULL"}
ROW_FIELDS = {"identity", "service", "replicate_index", "arm", "timepoint", "public_outcome",
              "endpoint_outcome", "complete_outcome", "domain_stratum"}
P0_FIELDS = {"identity", "public_outcome", "endpoint_outcome", "complete_outcome"}
require, encoded, digest = history.require, history.encoded, history.digest


def complete(public, endpoint):
    # This prospective analysis explicitly preserves any UNKNOWN component.
    if "UNKNOWN" in (public, endpoint):
        return "UNKNOWN"
    return "PASS" if public == endpoint == "PASS" else "FAIL"


def load_prospective(inputs):
    manifest = history.read_json(inputs / "manifest.json")
    require(manifest["schema_version"] == 2 and manifest["scope"] == "sanitized_analysis_replay_only", "v2 manifest")
    require(digest((HERE / "historical_replay.py").read_bytes()) == HISTORY_CODE_SHA, "historical replay source changed")
    expected = manifest["history_manifest"]
    raw_history = (inputs / "history/manifest.json").read_bytes()
    require(len(raw_history) == expected["bytes"] and digest(raw_history) == expected["sha256"], "historical manifest changed")
    p = manifest["prospective_input"]
    require(p["file"] == "prospective.json", "single fixed prospective input")
    raw = (inputs / p["file"]).read_bytes()
    require(len(raw) == p["bytes"] and digest(raw) == p["sha256"], "prospective input changed")
    data = json.loads(raw)
    require(data["schema_version"] == 2 and data["dataset"] == "quixbugs_prospective_two_task"
            and data["source_analysis"] == p["source_analysis"], "prospective identity/provenance")
    require(data["task_count"] == 2 and data["repetitions_per_service_task"] == 3
            and data["services"] == list(SERVICES), "two tasks, three repetitions per service")
    rows, p0 = data["rows"], data["P0"]
    require(len(rows) == 72 and len(p0) == 2, "complete delivery/P0 projection")
    expected_keys = {(t, s, r, a, p) for t in TASKS for s in SERVICES for r in REPS for a in ARMS for p in POINTS}
    keys = []
    for row in rows + p0:
        require(set(row) == (ROW_FIELDS if "service" in row else P0_FIELDS), "unexpected projected outcome fields")
        require(row["identity"] in TASKS, "fixed task identity")
        for f in ("public_outcome", "endpoint_outcome", "complete_outcome"):
            require(row[f] in history.OUTCOMES, "known outcome label")
        require(complete(row["public_outcome"], row["endpoint_outcome"]) == row["complete_outcome"], "C/H complete consistency")
        if "service" in row:
            require(type(row["replicate_index"]) is int and row["domain_stratum"] == STRATA[row["identity"]], "fixed repetition/domain stratum")
            keys.append(tuple(row[f] for f in ("identity", "service", "replicate_index", "arm", "timepoint")))
    require(len(set(keys)) == 72 and set(keys) == expected_keys, "all fixed logical aliases exactly once")
    require({r["identity"] for r in p0} == set(TASKS), "both P0 identities")
    return data, manifest


def summarize(data):
    index = {(r["identity"], r["service"], r["replicate_index"], r["arm"], r["timepoint"]): r for r in data["rows"]}
    tasks, pairs, aggregate = [], [], []
    for service in SERVICES:
        for point in POINTS:
            task_deltas = []
            for task in TASKS:
                counts = {}
                for arm in ARMS:
                    values = [index[(task, service, r, arm, point)]["complete_outcome"] for r in REPS]
                    counter = Counter(values)
                    counts[arm] = counter
                    tasks.append({"service": service, "timepoint": point, "identity": task,
                        "domain_stratum": STRATA[task], "arm": arm, "repetitions": 3,
                        "complete_pass": counter["PASS"], "complete_fail": counter["FAIL"],
                        "complete_unknown": counter["UNKNOWN"],
                        "task_mean_success": None if counter["UNKNOWN"] else counter["PASS"] / 3})
                deltas = []
                for rep in REPS:
                    outcomes = {a: index[(task, service, rep, a, point)]["complete_outcome"] for a in ARMS}
                    a, b = ("SEED", "CLOSURE") if task == TASKS[0] else ("CLOSURE", "FULL")
                    require(outcomes[a] == outcomes[b], "equal request classes must retain same outcome")
                    known = "UNKNOWN" not in (outcomes["SEED"], outcomes["FULL"])
                    delta = int(outcomes["SEED"] == "PASS") - int(outcomes["FULL"] == "PASS") if known else None
                    deltas.append(delta)
                    pairs.append({"service": service, "timepoint": point, "identity": task, "replicate_index": rep,
                        "domain_stratum": STRATA[task], **outcomes, "SEED_minus_FULL": delta,
                        "pair": "UNKNOWN" if delta is None else "SEED_win" if delta > 0 else "FULL_win" if delta < 0 else "tie"})
                task_deltas.append(sum(deltas) / 3 if all(d is not None for d in deltas) else None)
            group = [r for r in pairs if r["service"] == service and r["timepoint"] == point]
            pc = Counter(r["pair"] for r in group)
            aggregate.append({"service": service, "timepoint": point, "independent_tasks": 2,
                "repetitions_per_task": 3, "paired_task_repetitions_not_independent_tasks": 6,
                "mean_of_task_means_SEED_minus_FULL": sum(task_deltas) / 2 if all(d is not None for d in task_deltas) else None,
                "SEED_wins": pc["SEED_win"], "FULL_wins": pc["FULL_win"], "same_known_outcome": pc["tie"], "unknown_pairs": pc["UNKNOWN"]})
    return tasks, pairs, aggregate


def rebuild(inputs, output):
    require(inputs.resolve() != output.resolve(), "output must not overwrite inputs")
    data, manifest = load_prospective(inputs)
    old = history.rebuild(inputs / "history", output)
    require(old["aggregate_rows"] == 32, "historical 32 rows must remain separate and unchanged")
    tasks, pairs, aggregate = summarize(data)
    tables = {"prospective_identity_outcomes": data["rows"], "prospective_P0_outcomes": data["P0"],
        "prospective_task_means": tasks, "prospective_paired_repetitions": pairs,
        "prospective_paired_task_means": aggregate, "prospective_model_costs": data["model_costs"],
        "prospective_execution_costs": data["execution_costs"], "prospective_response_acceptance": data["response_acceptance"]}
    for name, rows in tables.items():
        history.csv_file(output / (name + ".csv"), rows)
    result = {"schema_version": 2, "scope": "prospective_analysis_replay_only", "population": data["population"],
        "task_count": 2, "repetitions_per_service_task": 3, "task_means": tasks,
        "all_paired_repetitions": pairs, "within_service_paired_task_means": aggregate,
        "model_costs": data["model_costs"], "execution_costs": data["execution_costs"],
        "response_acceptance": data["response_acceptance"], "new_model_calls": 0,
        "new_candidate_or_test_executions": 0, "significance_tests": [], "confidence_intervals": [],
        "cross_service_token_ratio": None, "independent_closure_expansion_claim": False}
    (output / "prospective_results.json").write_bytes(encoded(result))
    (output / "prospective_input_hashes.json").write_bytes(encoded(manifest))
    lines = ["# Prospective two-task repeated scope results", "",
        "The 40-algorithm intake yielded two tasks with different executable SEED/FULL permissions. These two tasks are the independent task denominator; three repetitions per service do not create six independent tasks.", "",
        "## Task-level repeated outcomes", "", "| Service | Delivery | Task | Policy | PASS / repetitions | UNKNOWN | Task mean |", "|---|---|---|---|---:|---:|---:|"]
    for r in tasks:
        lines.append(f"| {r['service']} | {r['timepoint']} | {r['identity']} | {r['arm']} | {r['complete_pass']}/3 | {r['complete_unknown']} | {r['task_mean_success']} |")
    lines += ["", "## Within-service SEED minus FULL", "", "| Service | Delivery | Tasks | Mean of task means | SEED wins | FULL wins | Ties | Unknown pairs |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in aggregate:
        lines.append(f"| {r['service']} | {r['timepoint']} | 2 | {r['mean_of_task_means_SEED_minus_FULL']} | {r['SEED_wins']} | {r['FULL_wins']} | {r['same_known_outcome']} | {r['unknown_pairs']} |")
    lines += ["", "The first-opportunity bank is primary; final two-opportunity delivery is secondary. The six paired repetition counts per service are descriptive, not six independent task observations.", "",
        "CLOSURE equals SEED for next_palindrome and FULL for pascal. No task has a selective intermediate closure, and this panel cannot isolate an incremental closure-expansion effect.", "",
        "The original 32 historical aggregate rows remain in core_results.*. They are not pooled with this panel. All 24 first/final task-repetition pairs, 72 delivery aliases and two P0 outcomes are retained in the separate CSV tables.", "",
        "Model-cost CSV rows distinguish physical calls from overlapping logical arm costs. Do not sum logical rows or compare raw token ratios between service tokenizers. Public execution, held-out execution and prior preparation have separate rows. Costs are copied from the closed accounting summary; this replay does not reconstruct per-request accounting from raw ledgers.", "",
        "Strict/normalized response acceptance is an interface diagnostic within the actual normalized trajectories. No alternative strict trajectory is reconstructed. No significance, equivalence or population superiority claim follows from two tasks.", ""]
    (output / "prospective_results.md").write_text("\n".join(lines), encoding="utf-8")
    return {"status": "analysis_replay_v2_complete", "historical_aggregate_rows": 32,
        "prospective_delivery_aliases": 72, "prospective_P0": 2, "prospective_tasks": 2,
        "prospective_task_mean_rows": len(tasks), "prospective_paired_repetition_rows": len(pairs),
        "new_model_calls": 0, "new_executions": 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=HERE / "inputs")
    parser.add_argument("--out", type=Path, default=HERE / "tables")
    args = parser.parse_args()
    print(json.dumps(rebuild(args.inputs, args.out), sort_keys=True))


if __name__ == "__main__":
    main()
