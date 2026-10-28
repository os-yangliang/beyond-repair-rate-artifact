"""Post-hoc task-paired bootstrap of public safe metadata; standard library only."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import random
import statistics
import sys

HERE = Path(__file__).resolve().parent
PLAN_SHA = "1e32a8814f34db9f8ceb347c9ea5007793ec17d26e9f907baf69907a73a2485a"
INPUT_SHA = "4502552cd74dd873252f4c9711dbe7fd402d3623559e8b48e3701723c95aae61"
SERVICES = ("qwen", "kimi")
METRICS = (
    "first_Tstar_difference_pp", "final_Tstar_difference_pp", "total_tokens_difference",
    "first_tokens_difference", "prepared_continuation_difference_pp",
    "actual_second_generation_difference_pp", "first_generation_HTTP_difference_seconds",
    "total_generation_HTTP_difference_seconds", "first_tokenizer_HTTP_difference_seconds",
    "total_tokenizer_HTTP_difference_seconds",
)
PRIMARY = METRICS[:3]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def load_inputs():
    plan_raw = (HERE / "analysis_plan.json").read_bytes()
    require(hashlib.sha256(plan_raw).hexdigest() == PLAN_SHA, "analysis plan changed")
    plan = json.loads(plan_raw)
    raw = (HERE / plan["source_file"]).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == INPUT_SHA == plan["source_sha256"], "input digest changed")
    data = json.loads(raw)
    require(data["source_analysis_sha256"] == plan["source_analysis_sha256"], "source-analysis mismatch")
    require(tuple(data["services"]) == SERVICES and data["replicates"] == [0, 1, 2], "design mismatch")
    tasks = sorted(data["tasks"], key=int)
    require(len(tasks) == len(set(tasks)) == 29 and "989" in tasks, "task frame mismatch")
    rows = data["rows"]
    keys = [(r["task"], r["service"], r["policy"], r["replicate"]) for r in rows]
    require(len(rows) == len(set(keys)) == 522, "duplicate or incomplete logical rows")
    expected = {(t,s,p,r) for t in tasks for s in SERVICES
                for p in ("C0_normalized", "C0_strict", "C1_normalized") for r in range(3)}
    require(set(keys) == expected, "missing design cells")
    lookup = dict(zip(keys, rows))
    require(all(r["first"] in ("PASS", "FAIL") and r["final"] in ("PASS", "FAIL")
                and r["unknown_usage_generations"] == 0 for r in rows), "unknown endpoints or usage")
    for row in rows:
        if row["policy"] == "C0_strict":
            twin = lookup[(row["task"], row["service"], "C0_normalized", row["replicate"])]
            require({k:v for k,v in row.items() if k != "policy"} ==
                    {k:v for k,v in twin.items() if k != "policy"}, "shared receiver rows differ")
    initial = data["initial"]
    require(len(initial) == 29 and {r["task"] for r in initial} == set(tasks), "initial frame mismatch")
    require(all(r["C0"] == "FAIL" and r["Tstar"] == "FAIL" for r in initial), "initial stratum mismatch")
    early = {r["task"] for r in initial if r["C1"] == "PASS"}
    require(len(early) == 6, "early-stop stratum mismatch")
    require({r["task"] for r in rows if r["total_status_counts"].get("budget_refusal", 0)} == {"989"},
            "local-refusal identity changed")
    return plan, data, tasks, early, lookup


def response_values(row):
    return (
        100 * int(row["first"] == "PASS"), 100 * int(row["final"] == "PASS"),
        row["total_tokens"], row["first_tokens"],
        100 * int(row["release_prepared"]), 100 * int(row["release_generated"]),
        row["first_generation_HTTP_seconds"], row["total_generation_HTTP_seconds"],
        row["first_tokenizer_HTTP_seconds"], row["total_tokenizer_HTTP_seconds"],
    )


def task_differences(tasks, early, lookup):
    detail = []
    for task in tasks:
        for service in SERVICES:
            rep_diffs = []
            for rep in range(3):
                c1 = response_values(lookup[(task,service,"C1_normalized",rep)])
                c0 = response_values(lookup[(task,service,"C0_normalized",rep)])
                rep_diffs.append([a-b for a,b in zip(c1,c0)])
            item = {"task":task, "service":service,
                    "baseline_stratum":"C1_P0_early_stop" if task in early else "repair_feedback",
                    "repetitions":3}
            item.update({m:statistics.fmean(r[j] for r in rep_diffs) for j,m in enumerate(METRICS)})
            detail.append(item)
    return detail


def quantile_type7(sorted_values, probability):
    h = (len(sorted_values) - 1) * probability
    low, high = math.floor(h), math.ceil(h)
    return sorted_values[low] + (h-low) * (sorted_values[high] - sorted_values[low])


def expected_points_check(detail):
    # Independently transcribed closed-study aggregate numerators, not inferred
    # from bootstrap outputs. Counts retain task-nested repetitions.
    totals = {
        ("all_tasks","qwen"):(29,24,40,35,50,529506,640387),
        ("all_tasks","kimi"):(29,18,24,20,29,492100,650587),
        ("repair_feedback","qwen"):(23,24,31,35,37,529506,505251),
        ("repair_feedback","kimi"):(23,18,18,20,19,492100,514590),
        ("C1_P0_early_stop","qwen"):(6,0,9,0,13,0,135136),
        ("C1_P0_early_stop","kimi"):(6,0,6,0,10,0,135997),
    }
    checks = []
    for (stratum, service), (n,a,b,c,d,e,f) in totals.items():
        rows = [r for r in detail if r["service"] == service and
                (stratum == "all_tasks" or r["baseline_stratum"] == stratum)]
        require(len(rows) == n, "point-estimate sample-size mismatch")
        expected = (100*(a-b)/(3*n),100*(c-d)/(3*n),(e-f)/(3*n))
        for metric, target in zip(PRIMARY,expected):
            actual = statistics.fmean(r[metric] for r in rows)
            require(math.isclose(actual,target,rel_tol=1e-12,abs_tol=1e-9), "closed point estimate mismatch")
            checks.append({"stratum":stratum,"service":service,"metric":metric,
                           "expected":target,"computed":actual,"passed":True})
    for service in SERVICES:
        for metric in METRICS:
            all_rows = [r for r in detail if r["service"] == service]
            early_rows = [r for r in all_rows if r["baseline_stratum"] == "C1_P0_early_stop"]
            feedback_rows = [r for r in all_rows if r["baseline_stratum"] == "repair_feedback"]
            weighted = (6*statistics.fmean(r[metric] for r in early_rows) +
                        23*statistics.fmean(r[metric] for r in feedback_rows))/29
            require(math.isclose(weighted, statistics.fmean(r[metric] for r in all_rows),
                                 rel_tol=1e-12,abs_tol=1e-8), "stratum decomposition mismatch")
    return checks


def bootstrap(plan, tasks, early, detail):
    rng = random.Random(plan["random_seed"])
    task_lookup = {(r["task"],r["service"]):r for r in detail}
    output, diagnostics, draw_hashes = [], [], {}
    for stratum in plan["resampling_strata_order"]:
        selected = tasks if stratum == "all_tasks" else [t for t in tasks if t not in early]
        n = len(selected)
        keys = [(s,m) for s in SERVICES for m in METRICS]
        vectors = [[task_lookup[(t,s)][m] for t in selected] for s,m in keys]
        samples = [[] for _ in keys]
        digest = hashlib.sha256()
        for _ in range(plan["bootstrap_repetitions"]):
            indices = rng.choices(range(n), k=n)
            digest.update((json.dumps(indices,separators=(",",":"))+"\n").encode("ascii"))
            weights = Counter(indices)
            for values, draws in zip(vectors,samples):
                draws.append(math.fsum(values[i]*count for i,count in weights.items())/n)
        draw_hashes[stratum] = digest.hexdigest()
        for (service,metric), values, draws in zip(keys,vectors,samples):
            estimate = statistics.fmean(values)
            ordered = sorted(draws)
            lower = quantile_type7(ordered,0.025)
            upper = quantile_type7(ordered,0.975)
            # An independent standard-library implementation of inclusive quantiles.
            other = statistics.quantiles(ordered,n=40,method="inclusive")
            require(math.isclose(lower,other[0],rel_tol=1e-12,abs_tol=1e-9) and
                    math.isclose(upper,other[-1],rel_tol=1e-12,abs_tol=1e-9), "quantile disagreement")
            exact_variance = statistics.pvariance(values)/n
            simulated_mean = statistics.fmean(draws)
            simulated_variance = statistics.pvariance(draws)
            degenerate = max(values) == min(values)
            if degenerate:
                require(all(math.isclose(x,estimate,rel_tol=1e-12,abs_tol=1e-10) for x in draws),
                        "degenerate vector changed under resampling")
                mean_z, variance_relative_error = None, None
            else:
                mean_z = abs(simulated_mean-estimate)/math.sqrt(exact_variance/len(draws))
                variance_relative_error = abs(simulated_variance/exact_variance-1)
                require(mean_z < 5 and variance_relative_error < 0.05, "bootstrap moment check failed")
            output.append({"stratum":stratum,"tasks":n,"repetitions_per_task":3,
                           "service":service,"metric":metric,"estimate_C1_minus_C0":estimate,
                           "lower_95_percentile":lower,"upper_95_percentile":upper,
                           "task_sample_sd":statistics.stdev(values),
                           "interval_degenerate":degenerate,
                           "distinct_task_differences":len(set(values)),
                           "bootstrap_draws":len(draws)})
            diagnostics.append({"stratum":stratum,"service":service,"metric":metric,
                                "exact_empirical_bootstrap_mean":estimate,
                                "observed_bootstrap_mean":simulated_mean,
                                "exact_empirical_bootstrap_variance":exact_variance,
                                "observed_bootstrap_variance":simulated_variance,
                                "mean_Monte_Carlo_z":mean_z,
                                "variance_relative_error":variance_relative_error,
                                "inclusive_quantiles_match":True,"passed":True})
    return output, diagnostics, draw_hashes


def markdown_table(results):
    lookup = {(r["stratum"],r["service"],r["metric"]):r for r in results}
    lines = ["| Service | Cohort (tasks) | First T* difference, pp [95% interval] | Final T* difference, pp [95% interval] | Total tokens per trajectory difference [95% interval] |",
             "|---|---|---:|---:|---:|"]
    for service in SERVICES:
        for stratum,n,label in (("all_tasks",29,"All selected"),("repair_feedback",23,"Repair feedback")):
            cells = [service.capitalize(),f"{label} ({n})"]
            for metric in PRIMARY:
                r = lookup[(stratum,service,metric)]
                cells.append(f"{r['estimate_C1_minus_C0']:+,.2f} [{r['lower_95_percentile']:+,.2f}, {r['upper_95_percentile']:+,.2f}]")
            lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def csv_text(rows):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output,fieldnames=list(rows[0]),lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def analyze():
    plan,data,tasks,early,lookup = load_inputs()
    detail = task_differences(tasks,early,lookup)
    point_checks = expected_points_check(detail)
    results,moments,draw_hashes = bootstrap(plan,tasks,early,detail)
    descriptive = []
    for service in SERVICES:
        selected = [r for r in detail if r["service"] == service and r["task"] in early]
        for metric in METRICS:
            values = [r[metric] for r in selected]
            descriptive.append({"stratum":"C1_P0_early_stop","tasks":6,"service":service,
                                "metric":metric,"estimate_C1_minus_C0":statistics.fmean(values),
                                "task_sample_sd":statistics.stdev(values),"minimum":min(values),
                                "maximum":max(values),"interval":"not_computed"})
    report = {"schema_version":1,"analysis_type":plan["analysis_type"],
              "analysis_plan_sha256":PLAN_SHA,"input_sha256":INPUT_SHA,
              "source_analysis_sha256":data["source_analysis_sha256"],
              "seed":plan["random_seed"],"bootstrap_repetitions":plan["bootstrap_repetitions"],
              "draw_index_stream_sha256":draw_hashes,
              "interval_method":"two-sided 95% percentile, type-7 linear interpolation",
              "results":results,"early_stop_descriptive_only":descriptive,
              "interpretation":plan["interpretation"],
              "model_calls":0,"candidate_or_test_executions":0,"network_requests":0}
    validation = {"status":"passed","source_hash_verified":True,"plan_hash_verified":True,
                  "tasks":29,"task_service_rows":len(detail),"logical_input_rows":522,
                  "primary_point_checks":point_checks,"stratum_decomposition_checks":20,
                  "bootstrap_quantile_and_moment_checks":moments,
                  "degenerate_interval_count":sum(r["interval_degenerate"] for r in results),
                  "all_29_tasks_retained":True,"local_refusal_task_989_retained":True,
                  "input_file_bytes_unchanged":True}
    encode = lambda x:json.dumps(x,indent=2,ensure_ascii=True,allow_nan=False)+"\n"
    return {"interval_results.json":encode(report),"interval_results.csv":csv_text(results),
            "task_differences.csv":csv_text(detail),"early_stop_descriptive.csv":csv_text(descriptive),
            "main_table.md":markdown_table(results),"validation.json":encode(validation)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,default=HERE/"results",help="New output directory; never overwrite")
    args = parser.parse_args()
    require(not args.out.exists(),"output directory exists; select a new destination")
    outputs = analyze()
    args.out.mkdir(parents=True,exist_ok=False)
    for name,text in outputs.items():
        with (args.out/name).open("x",encoding="utf-8",newline="\n") as stream:
            stream.write(text)
    print(json.dumps({"status":"passed","tasks":29,"repair_feedback_tasks":23,
                      "bootstrap_draws_per_stratum":20000,"outputs":list(outputs),
                      "model_calls":0,"candidate_or_test_executions":0}))


if __name__ == "__main__":
    if hasattr(sys.stdout,"reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
