from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from artifactproof.cli import run_validation


BENCHMARK_ROOT = Path(__file__).resolve().parent.parent / "benchmark"
RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"


def discover_benchmarks():
    tasks = []
    for requirement_file in sorted(BENCHMARK_ROOT.glob("*/requirement.yaml")):
        task_id = requirement_file.parent.name
        tasks.append(task_id)
    return tasks


def run_single_benchmark(task_id: str):
    root = BENCHMARK_ROOT / task_id
    requirement = root / "requirement.yaml"
    rows = []
    for impl in ["correct", "misdelivered"]:
        repo = root / impl
        output_dir = RESULTS_DIR / task_id / impl
        payload = run_validation(str(repo), str(requirement), str(output_dir))
        structural = payload["structural_validation"]
        causal = payload["causal_analysis"]
        baseline = payload["baseline"]
        row = {
            "task_id": task_id,
            "implementation_type": impl,
            "baseline_total_tests": baseline["total_tests"],
            "baseline_passed_tests": baseline["passed"],
            "structural_pass": structural["status"] == "PASS",
            "tests_affected_after_ablation": causal["tests_affected"],
            "artifact_causal_score": causal["artifact_causal_score"],
            "artifactproof_verdict": causal["status"],
            "expected_verdict": "CONFIRMED" if impl == "correct" else "SUSPICIOUS",
            "detection_correct": causal["status"] == ("CONFIRMED" if impl == "correct" else "SUSPICIOUS"),
        }
        rows.append(row)
    return rows


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for task_id in discover_benchmarks():
        rows.extend(run_single_benchmark(task_id))

    csv_path = RESULTS_DIR / "results.csv"
    json_path = RESULTS_DIR / "results.json"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "task_id",
            "implementation_type",
            "baseline_total_tests",
            "baseline_passed_tests",
            "structural_pass",
            "tests_affected_after_ablation",
            "artifact_causal_score",
            "artifactproof_verdict",
            "expected_verdict",
            "detection_correct",
        ])
        writer.writeheader()
        writer.writerows(rows)

    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    correct_scores = [row["artifact_causal_score"] for row in rows if row["implementation_type"] == "correct"]
    mis_scores = [row["artifact_causal_score"] for row in rows if row["implementation_type"] == "misdelivered"]
    summary = {
        "implementations_evaluated": len(rows),
        "normal_test_pass_rate": round(sum(1 for row in rows if row["baseline_passed_tests"] > 0) / len(rows), 4),
        "misdeliveries": sum(1 for row in rows if row["implementation_type"] == "misdelivered"),
        "artifactproof_detected": sum(1 for row in rows if row["detection_correct"]),
        "false_positives": sum(1 for row in rows if row["implementation_type"] == "correct" and not row["detection_correct"]),
        "false_negatives": sum(1 for row in rows if row["implementation_type"] == "misdelivered" and not row["detection_correct"]),
        "average_acs_correct": round(sum(correct_scores) / len(correct_scores), 4) if correct_scores else 0.0,
        "average_acs_misdelivered": round(sum(mis_scores) / len(mis_scores), 4) if mis_scores else 0.0,
    }
    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
