"""Offline arithmetic reproduction; Python 3.9+ and standard library only.
No models, candidate programs or tests run.
"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PACKAGES = ("historical_and_quixbugs", "bigcode_analysis", "bigcode_transitions")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def check_manifest():
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    require(manifest["schema_version"] == 1, "unsupported manifest version")
    files = manifest["files"]
    require(len(files) == manifest["copied_file_count"] == 38, "expected 38 copied files")
    names = [item["path"] for item in files]
    require(len(set(names)) == len(names), "duplicate manifest paths")
    for item in files:
        relative = Path(item["path"])
        require(not relative.is_absolute() and ".." not in relative.parts,
                "manifest paths must remain inside this artifact")
        require(relative.parts[0] in PACKAGES, "unexpected package")
        path = ROOT / relative
        require(not path.is_symlink(), "symlink is not a frozen copied file")
        raw = path.read_bytes()
        require(len(raw) == item["bytes"] and sha256(raw) == item["sha256"],
                "integrity mismatch: " + item["path"])
    for package in PACKAGES:
        expected = {name for name in names if name.startswith(package + "/")}
        actual = {p.relative_to(ROOT).as_posix()
                  for p in (ROOT / package).rglob("*") if p.is_file()}
        require(actual == expected, "unexpected or missing files in " + package)
    return files


def equivalent(expected, actual, suffix):
    if suffix == ".json":
        return json.loads(expected) == json.loads(actual)
    if suffix == ".csv":
        def rows(raw):
            return list(csv.reader(io.StringIO(raw.decode("utf-8"), newline="")))
        return rows(expected) == rows(actual)
    return expected.decode("utf-8").replace("\r\n", "\n") == actual.decode("utf-8").replace("\r\n", "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "reproduced",
                        help="new output directory; an existing directory is refused")
    args = parser.parse_args()
    require(sys.version_info >= (3, 9), "Python 3.9 or later is required")
    require(not sys.flags.optimize, "do not use -O: component assertions must remain enabled")
    out = args.out.resolve()
    require(not out.exists(), "output directory already exists; choose a new --out")
    for package in PACKAGES:
        require(out != ROOT / package and ROOT / package not in out.parents,
                "output cannot be inside a frozen package")
    out.mkdir(parents=True)
    report = {"schema_version": 1, "scope": "sanitized_analysis_reproduction_only",
              "status": "running", "copied_files_verified": 0,
              "commands": [], "comparisons": [], "new_model_calls": 0,
              "candidate_or_test_executions": 0, "network_requests": 0}
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    def run(label, relative_script, arguments=()):
        process = subprocess.run(
            [sys.executable, "-B", str(ROOT / relative_script), *map(str, arguments)],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out / (label + ".stdout.txt")).write_bytes(process.stdout)
        (out / (label + ".stderr.txt")).write_bytes(process.stderr)
        report["commands"].append({"entry_point": relative_script,
                                   "returncode": process.returncode,
                                   "stdout": label + ".stdout.txt",
                                   "stderr": label + ".stderr.txt"})
        require(process.returncode == 0, label + " failed; see preserved logs")
        return process.stdout

    def compare(label, expected, actual, suffix):
        equal = equivalent(expected, actual, suffix)
        report["comparisons"].append({"item": label, "passed": equal,
                                      "archived_sha256": sha256(expected),
                                      "rebuilt_sha256": sha256(actual)})
        require(equal, "rebuilt output differs: " + label)

    try:
        report["copied_files_verified"] = len(check_manifest())
        rebuilt = out / "historical_and_quixbugs_tables"
        run("historical_and_quixbugs", "historical_and_quixbugs/replay.py",
            ("--out", rebuilt))
        archived = ROOT / "historical_and_quixbugs/tables"
        expected_files = {p.name for p in archived.iterdir() if p.is_file()}
        actual_files = {p.name for p in rebuilt.iterdir() if p.is_file()}
        require(expected_files == actual_files, "historical table output file set differs")
        for name in sorted(expected_files):
            compare("historical_and_quixbugs/tables/" + name,
                    (archived / name).read_bytes(), (rebuilt / name).read_bytes(),
                    Path(name).suffix)
        analysis = run("bigcode_analysis", "bigcode_analysis/replay.py")
        compare("bigcode_analysis/replay_report.md",
                (ROOT / "bigcode_analysis/replay_report.md").read_bytes(), analysis, ".md")
        transitions = run("bigcode_transitions", "bigcode_transitions/reconstruct.py")
        # reconstruct.py prints an already newline-terminated report. Remove
        # exactly its extra console print terminator, not report whitespace.
        transitions = transitions.replace(b"\r\n", b"\n")
        require(transitions.endswith(b"\n"), "missing transition console terminator")
        transitions = transitions[:-1]
        compare("bigcode_transitions/tables.md",
                (ROOT / "bigcode_transitions/tables.md").read_bytes(), transitions, ".md")
        # Transition assertions and printed tables are replayed. The archived
        # machine-readable summary is integrity-checked, not silently regenerated.
        require(len(check_manifest()) == 38, "post-run integrity check failed")
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
    finally:
        (out / "verification.json").write_text(
            json.dumps(report, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"],
                      "copied_files_verified": report["copied_files_verified"],
                      "output_comparisons": len(report["comparisons"]),
                      "report": str(out / "verification.json"),
                      "new_model_calls": 0, "candidate_or_test_executions": 0}))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
