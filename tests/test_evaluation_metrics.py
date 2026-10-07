import json

from artifactproof.synthetic.cli import main
from artifactproof.synthetic.metrics import summarize_evaluations


def records() -> list[dict]:
    return [
        {
            "example_id": "heap-1",
            "structure": "heap",
            "expected": {"values": [2], "result": None},
            "predicted": {"values": [2], "result": None},
            "exact_match": True,
        },
        {
            "example_id": "heap-1",
            "structure": "heap",
            "expected": {"values": [2, 5], "result": None},
            "predicted": {"values": [5, 2], "result": None},
            "exact_match": False,
        },
        {
            "example_id": "dsu-1",
            "structure": "dsu",
            "expected": {"parents": [0, 0], "components": 1, "result": True},
            "predicted": None,
            "exact_match": False,
        },
    ]


def test_metric_summary_reports_multiple_granularities() -> None:
    summary = summarize_evaluations(records())

    assert summary["samples"] == 3
    assert summary["parse_rate"] == 0.666667
    assert summary["exact_match_accuracy"] == 0.333333
    assert summary["field_accuracy"] == 0.428571
    assert summary["sequence_accuracy"] == 0.0
    assert summary["by_structure"]["heap"]["exact_match_accuracy"] == 0.5


def test_metrics_cli_writes_json_report(tmp_path) -> None:
    source = tmp_path / "evaluations.jsonl"
    destination = tmp_path / "metrics.json"
    source.write_text("\n".join(json.dumps(item) for item in records()) + "\n")

    assert main(["metrics", "--input", str(source), "--output", str(destination)]) == 0
    assert json.loads(destination.read_text())["samples"] == 3


def test_empty_evaluation_has_zero_rates() -> None:
    summary = summarize_evaluations([])
    assert summary["samples"] == 0
    assert summary["exact_match_accuracy"] == 0.0
    assert summary["by_structure"] == {}
