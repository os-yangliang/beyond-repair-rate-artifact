"""Reconstruct closed-study transitions from safe metadata; no execution/network."""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

EXPECTED = "4502552cd74dd873252f4c9711dbe7fd402d3623559e8b48e3701723c95aae61"


def summarize(rows):
    count = lambda predicate: sum(bool(predicate(r)) for r in rows)
    p0 = count(lambda r: r["first_stop_reason"] == "P0_all_public_pass")
    p1 = count(lambda r: r["first_stop_reason"] == "own_bank_all_public_pass")
    stop = lambda r: r["first_stop_reason"] is not None
    out = {
        "tasks": len({r["task"] for r in rows}),
        "paired_task_repetitions": len(rows),
        "P0_public_early_stop": p0,
        "P0_public_stop_Tstar_pass": count(lambda r: r["first_stop_reason"] == "P0_all_public_pass" and r["first"] == "PASS"),
        "P0_public_stop_Tstar_fail": count(lambda r: r["first_stop_reason"] == "P0_all_public_pass" and r["first"] == "FAIL"),
        "R1_positions_prepared": sum(r["first_positions"] for r in rows),
        "R1_actual_generation": sum(r["first_generations"] for r in rows),
        "R1_local_admission_refusal": count(lambda r: r["first_response_status"] == "budget_refusal"),
        "R1_decoder_accepted": count(lambda r: r["first_decoder_accepted"] is True),
        "R1_decoder_rejected": count(lambda r: r["first_decoder_accepted"] is False),
        "R1_no_decoder": count(lambda r: r["first_decoder_accepted"] is None),
        "R1_public_all_pass_stop": p1,
        "R1_public_stop_Tstar_pass": count(lambda r: r["first_stop_reason"] == "own_bank_all_public_pass" and r["first"] == "PASS"),
        "R1_public_stop_Tstar_fail": count(lambda r: r["first_stop_reason"] == "own_bank_all_public_pass" and r["first"] == "FAIL"),
        "first_Tstar_pass": count(lambda r: r["first"] == "PASS"),
        "first_Tstar_fail": count(lambda r: r["first"] == "FAIL"),
        "prepared_continuation": count(lambda r: r["release_prepared"]),
        "actual_second_generation": count(lambda r: r["release_generated"]),
        "R2_local_admission_refusal": sum(r["total_status_counts"].get("budget_refusal", 0) - r["first_status_counts"].get("budget_refusal", 0) for r in rows),
        "R2_unsent_global_stop": count(lambda r: r["unsent_release_after_global_stop"]),
        "retained_stop_final_Tstar_pass": count(lambda r: stop(r) and r["final"] == "PASS"),
        "released_final_Tstar_pass": count(lambda r: r["release_prepared"] and r["final"] == "PASS"),
        "released_actual_final_Tstar_pass": count(lambda r: r["release_generated"] and r["final"] == "PASS"),
        "final_Tstar_pass": count(lambda r: r["final"] == "PASS"),
        "first_tokens": sum(r["first_tokens"] for r in rows),
        "total_tokens": sum(r["total_tokens"] for r in rows),
        "R2_tokens": sum(r["total_tokens"] - r["first_tokens"] for r in rows),
        "first_generation_HTTP_seconds": sum(r["first_generation_HTTP_seconds"] for r in rows),
        "total_generation_HTTP_seconds": sum(r["total_generation_HTTP_seconds"] for r in rows),
        "first_tokenizer_HTTP_seconds": sum(r["first_tokenizer_HTTP_seconds"] for r in rows),
        "total_tokenizer_HTTP_seconds": sum(r["total_tokenizer_HTTP_seconds"] for r in rows),
        "R1_response_status_counts": dict(Counter(r["first_response_status"] for r in rows)),
        "R1_decoder_rejection_counts": dict(Counter(r["first_decoder_reason"] for r in rows if r["first_decoder_accepted"] is False)),
    }
    n = out["paired_task_repetitions"]
    assert n == p0 + out["R1_positions_prepared"]
    assert out["R1_positions_prepared"] == out["R1_actual_generation"] + out["R1_local_admission_refusal"]
    assert out["R1_actual_generation"] == out["R1_decoder_accepted"] + out["R1_decoder_rejected"]
    assert n == p0 + p1 + out["prepared_continuation"]
    assert out["first_Tstar_fail"] == out["P0_public_stop_Tstar_fail"] + out["R1_public_stop_Tstar_fail"] + out["prepared_continuation"]
    assert out["prepared_continuation"] == out["actual_second_generation"] + out["R2_local_admission_refusal"]
    assert out["first_Tstar_pass"] == out["P0_public_stop_Tstar_pass"] + out["R1_public_stop_Tstar_pass"]
    assert out["final_Tstar_pass"] == out["retained_stop_final_Tstar_pass"] + out["released_final_Tstar_pass"]
    assert out["released_final_Tstar_pass"] == out["released_actual_final_Tstar_pass"]
    assert all(r["first"] in ["PASS", "FAIL"] and r["final"] in ["PASS", "FAIL"] for r in rows)
    assert all(not r["unknown_usage_generations"] for r in rows)
    assert all(not stop(r) or (not r["release_prepared"] and r["first"] == r["final"]) for r in rows)
    return out


def paired(rows, tasks, phase):
    key = lambda r: (r["task"], r["replicate"])
    c0 = {key(r): r for r in rows if r["policy"] == "C0_normalized" and r["task"] in tasks}
    c1 = {key(r): r for r in rows if r["policy"] == "C1_normalized" and r["task"] in tasks}
    assert set(c0) == set(c1)
    counts = Counter()
    detail = []
    for task in sorted(tasks, key=int):
        differences = []
        for rep in range(3):
            a, b = c1[(task, rep)][phase] == "PASS", c0[(task, rep)][phase] == "PASS"
            counts[(a, b)] += 1
            differences.append(int(a) - int(b))
        token_key = "first_tokens" if phase == "first" else "total_tokens"
        detail.append({"task": task, "C1_minus_C0_successes": sum(differences), "any_discordant_repetition": any(differences), "task_mean_difference": sum(differences) / 3, "C0_tokens": sum(c0[(task,r)][token_key] for r in range(3)), "C1_tokens": sum(c1[(task,r)][token_key] for r in range(3))})
    n = len(tasks)
    return {
        "tasks": n, "paired_task_repetitions": len(c0), "timepoint": phase,
        "both_pass": counts[(True, True)], "C1_only_pass": counts[(True, False)],
        "C0_only_pass": counts[(False, True)], "neither_pass": counts[(False, False)],
        "C1_pass": counts[(True, True)] + counts[(True, False)],
        "C0_pass": counts[(True, True)] + counts[(False, True)],
        "discordant_tasks": sum(r["any_discordant_repetition"] for r in detail),
        "C1_minus_C0_task_mean_percentage_points": 100 * sum(r["task_mean_difference"] for r in detail) / n,
        "C0_tokens": sum(r["C0_tokens"] for r in detail), "C1_tokens": sum(r["C1_tokens"] for r in detail),
        "C1_minus_C0_mean_task_repeat_tokens": sum(r["C1_tokens"] - r["C0_tokens"] for r in detail) / (3 * n),
        "task_details": detail,
    }


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] + ["| " + " | ".join(str(v) for v in r) + " |" for r in rows])


def render(result):
    out = ["# BigCodeBench public-stop transitions and partition strata", "", "This is an arithmetic audit of safe metadata, with no new model, candidate, or test execution. Counts are task–repetition observations unless explicitly marked tasks. Each service has 29 tasks and three within-task repetitions. T* was evaluated after sealing and never controlled continuation.", "", "## First opportunity and decoder accounting", ""]
    out += [table(["Service", "Public pool", "P0 public stop", "R1 prepared", "R1 actual", "R1 local refusal", "Decoder accept / reject", "R1 public stop: T* pass / fail"], [[r["service"],r["partition"],r["P0_public_early_stop"],r["R1_positions_prepared"],r["R1_actual_generation"],r["R1_local_admission_refusal"],str(r["R1_decoder_accepted"])+" / "+str(r["R1_decoder_rejected"]),str(r["R1_public_stop_Tstar_pass"])+" / "+str(r["R1_public_stop_Tstar_fail"])] for r in result["transitions"]]), "", "## Release reconstruction", ""]
    out += [table(["Service", "Pool", "First T* pass", "First T* fail", "P0 stop T* fail", "R1 public stop T* fail", "Prepared R2", "Actual R2", "Local R2 refusal", "Final T* pass: retained + release"], [[r["service"],r["partition"],r["first_Tstar_pass"],r["first_Tstar_fail"],r["P0_public_stop_Tstar_fail"],r["R1_public_stop_Tstar_fail"],r["prepared_continuation"],r["actual_second_generation"],r["R2_local_admission_refusal"],str(r["final_Tstar_pass"])+": "+str(r["retained_stop_final_Tstar_pass"])+" + "+str(r["released_final_Tstar_pass"])] for r in result["transitions"]]), "", "For every row: first T* fail = P0-public-stop/T*-fail + R1-public-stop/T*-fail + prepared R2. Prepared R2 = actual R2 + local admission refusal. Final T* pass = retained public-stop success + success after a release generation. Qwen C0 therefore has 47 first T* failures but only 39 releases: eight first deliveries already pass C0 and stop while failing T*. C1 adds 18 P0 early-stopped observations (six tasks × three repetitions), all T*-failing.", "", "Strict and normalized C0 branches share these exact counts, delivery outcomes, and logical costs. They are one row here, not additive spending. Refusal means no API generation was sent; it is not a decoder rejection. All local refusals occur on task 989, for three repetitions in both pools and both opportunities. No unsent global-stop positions or selected-task UNKNOWN outcomes remain.", "", "## Partition outcomes by baseline stopping stratum", "", "The six-task stratum is fixed by C1 P0 public passage, before any repair generation: " + ", ".join(result["early_stop_tasks"]) + ". The remaining 23 tasks have repair-feedback trajectories under both public pools. All 29 were selected conditional on C0 failure. These are descriptive strata, not randomized populations or forced-generation counterfactuals.", ""]
    out += [table(["Service", "Stratum (tasks)", "Phase", "C1 / C0 successes", "Both / C1 only / C0 only / neither", "Discordant tasks", "C1 − C0 pp"], [[r["service"],r["stratum"]+" ("+str(r["tasks"])+")",r["timepoint"],str(r["C1_pass"])+" / "+str(r["C0_pass"])," / ".join(str(r[k]) for k in ["both_pass","C1_only_pass","C0_only_pass","neither_pass"]),r["discordant_tasks"],format(r["C1_minus_C0_task_mean_percentage_points"],".2f")] for r in result["stratum_pairs"]]), "", "## Logical generation costs by stratum", ""]
    out += [table(["Service", "Stratum (tasks)", "Pool", "R1 gen", "R2 prepared / actual", "R1 tokens", "R2 tokens", "Total tokens", "Generation HTTP s"], [[r["service"],r["stratum"]+" ("+str(r["tasks"])+")",r["partition"],r["R1_actual_generation"],str(r["prepared_continuation"])+" / "+str(r["actual_second_generation"]),r["first_tokens"],r["R2_tokens"],r["total_tokens"],format(r["total_generation_HTTP_seconds"],".3f")] for r in result["stratum_transitions"]]), "", "Tokens are provider-reported generation usage, not dollars; execution costs remain in the complete study accounting. HTTP seconds are observed acquisition components, not end-to-end or pure inference latency. C0-normalized is reused by interface and partition comparisons, and strict C0 is shared, so these rows must not be summed across experiments/policies to reconstruct physical spending.", "", "## Task-weighted paired cost differences", ""]
    out += [table(["Service", "Stratum", "Phase", "C0 tokens", "C1 tokens", "C1 − C0 tokens per task–repeat"], [[r["service"],r["stratum"],r["timepoint"],r["C0_tokens"],r["C1_tokens"],format(r["C1_minus_C0_mean_task_repeat_tokens"],".2f")] for r in result["stratum_pairs"]]), "", "All arithmetic identities and stratum-to-total sums are asserted by reconstruct.py. Repetitions remain nested within tasks; no p-values, equivalence tests, or population confidence intervals are manufactured.", ""]
    return "\n".join(out)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Create outputs exclusively; refuse to overwrite")
    args = parser.parse_args()
    folder = Path(__file__).resolve().parent
    raw = (folder / "safe_projection.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == EXPECTED
    data = json.loads(raw)
    rows, tasks = data["rows"], set(data["tasks"])
    assert len(tasks) == 29 and len(rows) == 522 and data["replicates"] == [0, 1, 2]
    assert len({(r["task"], r["service"], r["policy"], r["replicate"]) for r in rows}) == 522
    assert {r["task"] for r in rows if r["total_status_counts"].get("budget_refusal", 0)} == {"989"}
    lookup = {(r["task"], r["service"], r["policy"], r["replicate"]): r for r in rows}
    for r in rows:
        if r["policy"] == "C0_strict":
            twin = lookup[(r["task"], r["service"], "C0_normalized", r["replicate"])]
            assert {k:v for k,v in r.items() if k != "policy"} == {k:v for k,v in twin.items() if k != "policy"}
    early = {r["task"] for r in data["initial"] if r["C1"] == "PASS"}
    assert len(early) == 6 and all(r["C0"] == "FAIL" and r["Tstar"] == "FAIL" for r in data["initial"])
    strata = {"C1_P0_early_stop": early, "repair_feedback": tasks - early}
    result = {"schema_version":1,"source_analysis_sha256":data["source_analysis_sha256"],"projection_sha256":EXPECTED,"early_stop_tasks":sorted(early,key=int),"transitions":[],"stratum_transitions":[],"stratum_pairs":[],"interpretation":"conditional on C0 failure; six C1 P0 stop tasks and 23 repair-feedback tasks; not forced-generation counterfactuals"}
    for service in data["services"]:
        service_rows = [r for r in rows if r["service"] == service]
        for part in ["C0", "C1"]:
            policy = part + "_normalized"
            selected = [r for r in service_rows if r["policy"] == policy]
            r = summarize(selected)
            result["transitions"].append(dict(service=service,partition=part,**r))
            by_stratum = []
            for name, members in strata.items():
                sr = summarize([x for x in selected if x["task"] in members])
                by_stratum.append(sr)
                result["stratum_transitions"].append(dict(service=service,partition=part,stratum=name,**sr))
            for field, value in r.items():
                if isinstance(value, int):
                    assert value == sum(x[field] for x in by_stratum), (service,part,field)
        for name, members in strata.items():
            for phase in ["first", "final"]:
                result["stratum_pairs"].append(dict(service=service,stratum=name,**paired(service_rows,members,phase)))
        for phase in ["first", "final"]:
            overall = paired(service_rows,tasks,phase)
            selected = [r for r in result["stratum_pairs"] if r["service"]==service and r["timepoint"]==phase]
            for field in ["both_pass","C1_only_pass","C0_only_pass","neither_pass","C1_pass","C0_pass","C0_tokens","C1_tokens"]:
                assert overall[field] == sum(r[field] for r in selected)
    report = render(result)
    if args.write:
        outputs = [folder / "transition_summary.json", folder / "tables.md"]
        assert all(not p.exists() for p in outputs), "outputs exist; exclusive creation only"
        with outputs[0].open("x",encoding="utf-8",newline="\n") as f:
            json.dump(result,f,ensure_ascii=True,indent=2);f.write("\n")
        with outputs[1].open("x",encoding="utf-8",newline="\n") as f:
            f.write(report)
    print(report)


if __name__ == "__main__":
    main()
