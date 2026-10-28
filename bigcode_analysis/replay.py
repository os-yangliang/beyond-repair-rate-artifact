"""Arithmetic replay of the frozen safe projection; Python standard library only."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT_SHA = "902ab00dddaac937b841e0c4b4c97759d377d1077ae817c3bbf4f212e3cf741c"
SOURCE_SHA = "0e70311d0073b2ff0a95c879244b20936dd41b85668175731a554147d8787650"
SERVICES = ("qwen", "kimi")
POLICIES = ("C0_normalized", "C0_strict", "C1_normalized")


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def table(title, header, rows):
    return ["", "## " + title, "", "| " + " | ".join(header) + " |",
            "| " + " | ".join("---" for _ in header) + " |"] + [
                "| " + " | ".join(map(str, row)) + " |" for row in rows]


def replay():
    raw = (HERE / "safe_projection.json").read_bytes()
    require(hashlib.sha256(raw).hexdigest() == INPUT_SHA, "projection_hash")
    a = json.loads(raw)
    require(a["source_analysis_sha256"] == SOURCE_SHA and a["schema_version"] == 1, "source_identity")
    tasks, reps = a["tasks"], a["replicates"]
    require(a["A_tasks"] == 0 and len(tasks) == len(set(tasks)) == 29 and reps == [0, 1, 2], "fixed_population")
    require(a["services"] == list(SERVICES) and a["policies"] == list(POLICIES), "fixed_design")
    index = {(r["task"], r["service"], r["replicate"], r["policy"]): r for r in a["rows"]}
    expected = {(t, s, r, p) for t in tasks for s in SERVICES for r in reps for p in POLICIES}
    require(len(index) == len(a["rows"]) == 522 and set(index) == expected, "all_logical_branches")
    require(all(r[p] in ("PASS", "FAIL") for r in index.values() for p in ("first", "final"))
            and a["declared_summary"]["unknown_endpoint_programs"] == 0, "known_complete_endpoints")
    require(all(r["unknown_usage_generations"] == 0 for r in index.values()), "known_usage")
    initials = {r["task"]: r for r in a["initial"]}
    require(set(initials) == set(tasks), "all_initial_programs")
    early = {t for t, r in initials.items() if r["C1"] == "PASS"}
    require(len(early) == 6 and all(initials[t]["Tstar"] == "FAIL" for t in early), "early_stop_status")
    lines = ["# BigCodeBench safe-summary arithmetic replay", "",
             "Local, unpublished metadata subset. A = 0; B and C use the same 29 tasks.",
             "Three repetitions are nested within task. Services remain separate. No model or test was rerun.",
             "Input SHA-256: `" + INPUT_SHA + "`.",
             "Source safe-analysis SHA-256: `" + SOURCE_SHA + "`."]

    t13 = []
    for s in SERVICES:
        for p in ("C0_normalized", "C1_normalized"):
            rows = [index[(t, s, r, p)] for t in tasks for r in reps]
            first = sum(x["first"] == "PASS" for x in rows)
            final = sum(x["final"] == "PASS" for x in rows)
            tokens = sum(x["total_tokens"] for x in rows)
            release = sum(x["release_generated"] for x in rows)
            prepared = sum(x["release_prepared"] for x in rows)
            require(all(x["total_generations"] - x["first_generations"] == int(x["release_generated"])
                        and x["total_positions"] - x["first_positions"] == int(x["release_prepared"]) for x in rows),
                    "two_opportunity_cost_accounting")
            if p == "C0_normalized":
                for t in tasks:
                    for r in reps:
                        l, q = index[(t, s, r, p)], index[(t, s, r, "C0_strict")]
                        for field in ("first", "final", "first_tokens", "total_tokens", "first_generations", "total_generations",
                                      "total_positions", "release_prepared", "release_generated", "first_decoder_accepted"):
                            require(l[field] == q[field], "recorded_interface_rows_coincide")
                        require(l["same_interface_source_first"] and l["same_interface_source_final"], "same_interface_deliveries")
            t13.append([s, "C0 strict = normalized" if p.startswith("C0") else "C1 normalized",
                        first, final, "%d / %d" % (release, prepared), f"{tokens:,}", f"{tokens/final:,.1f}"])
    lines += table("Table 13: complete T* delivery and logical continuation cost",
        ["Service", "Policy", "First / 87", "Final / 87", "Actual / prepared release", "Total tokens", "Tokens / final pass"], t13)
    lines += ["", "Tokens include unsuccessful trajectories. Logical policy rows overlap; do not sum them as physical spending."]

    comparisons, t14 = {}, []
    for experiment, left in (("B", "C0_normalized"), ("C", "C1_normalized")):
        right = "C0_strict" if experiment == "B" else "C0_normalized"
        for s in SERVICES:
            for point, oldpoint in (("first", "first_opportunity"), ("final", "final_delivery")):
                counts, diffs, discordant_tasks, discordant_pairs = Counter(), {}, set(), 0
                for t in tasks:
                    vals = []
                    for r in reps:
                        l, q = index[(t, s, r, left)][point], index[(t, s, r, right)][point]
                        counts[(l, q)] += 1
                        vals.append(int(l == "PASS") - int(q == "PASS"))
                        if l != q:
                            discordant_tasks.add(t); discordant_pairs += 1
                    diffs[t] = sum(vals)
                effect = sum(v / 3 for v in diffs.values()) / len(tasks)
                declared = next(v for v in a["declared_summary"]["comparisons"]
                    if (v["experiment"], v["service"], v["timepoint"]) == (experiment, s, oldpoint))
                require(math.isclose(effect, declared["task_weighted_point_difference"], abs_tol=1e-12)
                    and discordant_pairs == declared["known_discordant_replicates"]
                    and len(discordant_tasks) == declared["tasks_with_known_discordance"], "recomputed_paired_summary")
                comparisons[(experiment, s, point)] = {"diffs": diffs, "discordant_tasks": discordant_tasks}
                if experiment == "C":
                    pattern = [counts[k] for k in (("PASS", "PASS"), ("PASS", "FAIL"), ("FAIL", "PASS"), ("FAIL", "FAIL"))]
                    t14.append([s, point, f"{100*effect:.2f}", " / ".join(map(str, pattern)), f"{len(discordant_tasks)} / 29"])
    lines += table("Table 15: C1-minus-C0 paired complete outcomes",
        ["Service", "Delivery", "Task mean difference (pp)", "Both / C1 only / C0 only / neither", "Discordant tasks"], t14)
    lines += ["", "Effects average three paired repetitions within each task, then weight tasks equally. No confidence interval or equivalence claim is computed."]

    physical = a["physical_service_round"]
    require({(x["service"], x["round"]) for x in physical} == {(s, r) for s in SERVICES for r in (1, 2)}
            and len(physical) == 4, "four_physical_ledgers")
    t15 = []
    for s in SERVICES:
        rs = [r for r in physical if r["service"] == s]
        gen = sum(r["generation_attempts"] for r in rs)
        tok = sum(r["tokenizer_attempts"] for r in rs)
        refused = sum(r["status_counts"].get("budget_refusal", 0) for r in rs)
        tokens = sum(r["known_reported_usage"]["total_tokens"] for r in rs)
        require(sum(r["physical_request_positions"] for r in rs) == gen + refused, "physical_refusal_separation")
        t15.append([s, gen, tok, refused, f"{tokens:,}",
                    f"{sum(r['generation_HTTP_seconds'] for r in rs):,.3f}",
                    f"{sum(r['tokenizer_HTTP_seconds'] for r in rs):,.3f}"])
    declared = a["declared_summary"]["physical_total"]
    for field in ("generation_attempts", "tokenizer_attempts", "physical_request_positions", "unknown_usage_generation_attempts"):
        require(sum(r[field] for r in physical) == declared[field], "physical_total_" + field)
    for token in ("prompt_tokens", "completion_tokens", "total_tokens"):
        require(sum(r["known_reported_usage"][token] for r in physical) == declared["known_reported_usage"][token], "token_sum")
    lines += table("Table 17: actual physical acquisition",
        ["Service", "Generations", "Tokenizer", "Local unsent", "Reported tokens", "Generation HTTP (s)", "Tokenizer HTTP (s)"], t15)
    lines += ["", f"Total reported generation tokens: {declared['known_reported_usage']['total_tokens']:,}; unknown usage: 0.",
              f"Collection-stage wall time: {a['collection_wall_seconds']:,.3f} s. HTTP components are not pure inference or end-to-end latency; provider token units are not a common currency."]

    affected = set().union(*(v["discordant_tasks"] for k, v in comparisons.items() if k[0] == "C"))
    g1 = []
    for t in sorted(affected, key=int):
        g1.append([t + (" *" if t in early else "")] + [
            "%+d" % comparisons[("C", s, p)]["diffs"][t] if comparisons[("C", s, p)]["diffs"][t] else "0"
            for s in SERVICES for p in ("first", "final")])
    lines += table("Table G1: task-level differences across three repetitions",
        ["Task", "Qwen first", "Qwen final", "Kimi first", "Kimi final"], g1)
    lines += ["", "* C1 initial all-pass and P0 early stopping. Unlisted tasks have no paired outcome discordance."]
    for s in SERVICES:
        for p in ("first", "final"):
            diff = comparisons[("C", s, p)]["diffs"]
            lines.append(f"- {s} {p}: six early-stop tasks contribute {sum(diff[t] for t in early):+d}; other 23 contribute {sum(diff[t] for t in tasks if t not in early):+d}.")

    buckets = {"integration": [], "initial_C0": [], "C1_P0": [], "candidate_public": [], "endpoint": []}
    for row in a["execution_stages"]:
        name = "candidate_public" if row["component"].startswith("candidate_round") else row["component"]
        require(name in buckets, "known_execution_component")
        buckets[name].append(row)
    g2, totals = [], {"jobs": 0, "cli_calls": 0, "stage_seconds": 0.0}
    for label, rs in buckets.items():
        require(rs, "complete_execution_account")
        values = {k: sum(r[k] for r in rs) for k in totals}
        for k in totals:
            totals[k] += values[k]
        g2.append([label, f"{values['jobs']:,}", f"{values['cli_calls']:,}", f"{values['stage_seconds']:,.3f}"])
    total = a["declared_summary"]["execution_total"]
    require(totals["jobs"] == total["jobs"] and totals["cli_calls"] == total["cli_calls"]
            and math.isclose(totals["stage_seconds"], total["execution_stage_elapsed_seconds_sum"], abs_tol=1e-8), "execution_totals")
    g2.append(["Total", f"{totals['jobs']:,}", f"{totals['cli_calls']:,}", f"{totals['stage_seconds']:,.3f}"])
    lines += table("Table G2: full physical execution account", ["Component", "Jobs", "CLI", "Stage seconds"], g2)
    lines += ["", f"Endpoint reused {a['endpoint_public_vector_reuse']} public vectors with zero new jobs for those observations.",
        "The initial resource failure and all controls remain included. Stage seconds are summed accounting components, not end-to-end research latency.",
        "", "## Scope", "", "All displayed arithmetic agrees with the projected safe-analysis summaries. This does not independently authenticate raw requests, source code, test execution, the scientific oracle or model behavior. The subset has not been publicly released; no project or third-party license is assigned here."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-report", action="store_true", help="Create replay_report.md once; otherwise print it.")
    args = parser.parse_args()
    report = replay()
    if args.write_report:
        target = HERE / "replay_report.md"
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(report)
        print(json.dumps({"status": "metadata_arithmetic_reproduced", "tasks": 29, "A_tasks": 0,
            "tables": ["13", "14", "15", "G1", "G2"], "input_sha256": INPUT_SHA,
            "report_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "model_calls": 0, "candidate_or_test_executions": 0}))
    else:
        print(report, end="")
