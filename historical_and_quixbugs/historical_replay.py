"""Rebuild article tables from portable, sanitized outcome metadata only.

Python standard library only. This module does not import project code, contact
services, or load/execute candidate programs, prompts, or test bodies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUTCOMES = {"PASS", "FAIL", "UNKNOWN"}
ROW_FIELDS = {"identity", "assignment", "arm", "timepoint", "contract",
              "public_outcome", "endpoint_outcome", "complete_outcome",
              "domain_stratum", "public_stratum"}
GROUP = ("dataset", "service", "timepoint", "contract", "arm")


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def complete(public, endpoint):
    if "FAIL" in (public, endpoint):
        return "FAIL"
    return "PASS" if public == endpoint == "PASS" else "UNKNOWN"


def load_inputs(folder):
    manifest_path = folder / "manifest.json"
    manifest = read_json(manifest_path)
    require(manifest["schema_version"] == 1, "Unsupported input manifest")
    datasets, pins = [], []
    for item in manifest["inputs"]:
        name = item["file"]
        require(Path(name).name == name and name.endswith(".json"), "Input must be a local JSON filename")
        path = folder / name
        raw = path.read_bytes()
        require(len(raw) == item["bytes"] and digest(raw) == item["sha256"], "Input hash mismatch: " + name)
        data = json.loads(raw)
        require(data["source_analysis"] == item["source_analysis"], "Source provenance mismatch")
        require(data["schema_version"] == 1 and data["dataset"] == item["dataset"], "Input identity mismatch")
        seen = set()
        for row in data["rows"]:
            require(set(row) == ROW_FIELDS, "Unexpected outcome projection fields")
            require(row["arm"] in data["arm_order"], "Unknown policy")
            key = (row["identity"], row["arm"], row["timepoint"], row["contract"])
            require(key not in seen, "Duplicate logical observation")
            seen.add(key)
            for field in ("public_outcome", "endpoint_outcome", "complete_outcome"):
                require(row[field] in OUTCOMES, "Unsupported outcome")
            require(complete(row["public_outcome"], row["endpoint_outcome"]) == row["complete_outcome"],
                    "Complete result disagrees with public/endpoint outcomes")
        require(len({r["identity"] for r in data["rows"]}) == data["row_identity_count"], "Identity projection mismatch")
        if "service_groups" in data:
            require(len({r["identity"].split(":", 1)[1] for r in data["rows"]}) == data["task_count"],
                    "Shared task count must not count services as new tasks")
        else:
            require(data["row_identity_count"] == data["task_count"], "Task denominator mismatch")
        datasets.append(data)
        pins.append(item)
    require(len(datasets) == 6, "Expected six explicitly projected analysis inputs")
    return datasets, {"manifest_sha256": digest(manifest_path.read_bytes()), "inputs": pins}


def summarize(datasets):
    aggregate, identities, paired = [], [], []
    panels = []
    for data in datasets:
        if "service_groups" not in data:
            panels.append(data)
            continue
        for service in data["service_groups"]:
            prefix = service + ":"
            panel = dict(data)
            panel["service"] = service
            panel["rows"] = [{**r, "identity": r["identity"][len(prefix):]}
                             for r in data["rows"] if r["identity"].startswith(prefix)]
            require(len({r["identity"] for r in panel["rows"]}) == panel["task_count"], "Incomplete service panel")
            panel["reported_aggregates"] = [r for r in data["reported_by_service"] if r["service"] == service]
            panels.append(panel)
    for data in panels:
        grouped = defaultdict(list)
        for row in data["rows"]:
            identities.append({"dataset": data["dataset"], "service": data["service"], **row})
            grouped[(row["timepoint"], row["contract"], row["arm"])].append(row)
        for key, rows in grouped.items():
            counts = Counter(r["complete_outcome"] for r in rows)
            require(len(rows) == data["task_count"], "Incomplete treatment denominator")
            aggregate.append({"dataset": data["dataset"], "service": data["service"],
                              "timepoint": key[0], "contract": key[1], "arm": key[2],
                              "N": len(rows), "complete_pass": counts["PASS"],
                              "complete_fail": counts["FAIL"], "complete_unknown": counts["UNKNOWN"]})
        for expectation in data["reported_aggregates"]:
            matches = [r for r in aggregate if r["dataset"] == data["dataset"] and r["service"] == data["service"]
                       and all(r[k] == expectation[k] for k in ("timepoint", "contract", "arm"))]
            require(len(matches) == 1 and all(matches[0][k] == expectation[k]
                    for k in ("N", "complete_pass")), "Projected identities disagree with archived aggregate")
        for point, contract in sorted({k[:2] for k in grouped}):
            control = {r["identity"]: r["complete_outcome"]
                       for r in grouped[(point, contract, data["control_arm"]) ]}
            for arm in data["arm_order"]:
                if arm == data["control_arm"]:
                    continue
                left = {r["identity"]: r["complete_outcome"] for r in grouped[(point, contract, arm)]}
                require(set(left) == set(control), "Unpaired identities")
                known = [(left[i], control[i]) for i in left if "UNKNOWN" not in (left[i], control[i])]
                paired.append({"dataset": data["dataset"], "service": data["service"],
                               "timepoint": point, "contract": contract, "arm": arm,
                               "control": data["control_arm"], "N": len(left),
                               "arm_only_pass": sum(a == "PASS" and b == "FAIL" for a, b in known),
                               "control_only_pass": sum(a == "FAIL" and b == "PASS" for a, b in known),
                               "same_known_outcome": sum(a == b for a, b in known),
                               "unknown_pairs": len(left) - len(known)})
    return aggregate, identities, paired


def csv_file(path, rows):
    require(bool(rows), "Cannot render an empty table")
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def table(rows):
    lines = ["| Dataset | Service | Timepoint | Contract | Policy | Complete / N | UNKNOWN |",
             "|---|---|---|---|---|---:|---:|"]
    for r in rows:
        lines.append("| {dataset} | {service} | {timepoint} | {contract} | {arm} | "
                     "{complete_pass}/{N} | {complete_unknown} |".format(**r))
    return lines


def rebuild(inputs, output):
    datasets, provenance = load_inputs(inputs)
    aggregate, identities, paired = summarize(datasets)
    output.mkdir(parents=True, exist_ok=True)
    csv_file(output / "core_results.csv", aggregate)
    csv_file(output / "identity_outcomes.csv", identities)
    csv_file(output / "paired_outcomes.csv", paired)
    results = {"schema_version": 1, "scope": "analysis_replay_only",
               "new_model_calls": 0, "new_candidate_or_test_executions": 0,
               "pooled_population_effect": False, "core_results": aggregate,
               "paired_outcomes": paired, "identity_outcomes": identities}
    (output / "core_results.json").write_bytes(encoded(results))
    (output / "input_hashes.json").write_bytes(encoded(provenance))
    lines = ["# Rebuilt article results", "",
             "Recomputed from sanitized identity-level outcome metadata. No model, candidate, or test is run.", "",
             "## Original Refactory studies", ""]
    lines += table([r for r in aggregate if r["dataset"].startswith("study_")])
    lines += ["", "These three developmental populations share assignment families and are not pooled.", "",
              "## Original external repair trajectories", ""]
    lines += table([r for r in aggregate if r["dataset"].startswith("external_")])
    lines += ["", "The services use the same ten inputs; repeated arms and services do not create new tasks.", "",
              "## Archived first-response formatting diagnostic", ""]
    lines += table([r for r in aggregate if r["dataset"] == "format_first_response"])
    lines += ["", "The normalized rows concern fixed first responses only. They are not new two-round trajectories,",
              "and do not estimate saved calls or tokens. Original and normalized rows are paired observations.", "",
              "`identity_outcomes.csv` retains every projected identity, including unsuccessful and UNKNOWN outcomes.",
              "`paired_outcomes.csv` reports paired counts without significance or equivalence claims.", "",
              "See `input_hashes.json` for both the portable input hashes and original analysis-file hashes.", ""]
    (output / "core_results.md").write_text("\n".join(lines), encoding="utf-8")
    return {"status": "analysis_replay_complete", "input_files": len(datasets),
            "aggregate_rows": len(aggregate), "identity_rows": len(identities),
            "new_model_calls": 0, "new_executions": 0,
            "output_files": [p.name for p in sorted(output.iterdir()) if p.is_file()]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=HERE / "inputs")
    parser.add_argument("--out", type=Path, default=HERE / "tables")
    args = parser.parse_args()
    require(args.inputs.resolve() != args.out.resolve(), "Outputs must not overwrite inputs")
    print(json.dumps(rebuild(args.inputs, args.out), sort_keys=True))


if __name__ == "__main__":
    main()
