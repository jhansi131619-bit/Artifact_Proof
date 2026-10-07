"""Automated metrics for multimodal state predictions."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from .evaluation import EvaluationRecord

EvaluationLike = EvaluationRecord | Mapping[str, Any]


def _value(record: EvaluationLike, key: str) -> Any:
    return getattr(record, key) if isinstance(record, EvaluationRecord) else record[key]


def summarize_evaluations(records: Iterable[EvaluationLike]) -> dict[str, Any]:
    items = list(records)
    total = len(items)
    parsed = sum(_value(item, "predicted") is not None for item in items)
    exact = sum(bool(_value(item, "exact_match")) for item in items)
    field_total = 0
    field_correct = 0
    structure_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    example_matches: dict[str, list[bool]] = defaultdict(list)

    for item in items:
        structure = str(_value(item, "structure"))
        matched = bool(_value(item, "exact_match"))
        structure_counts[structure][0] += 1
        structure_counts[structure][1] += int(matched)
        example_matches[str(_value(item, "example_id"))].append(matched)
        expected = _value(item, "expected")
        predicted = _value(item, "predicted") or {}
        field_total += len(expected)
        field_correct += sum(predicted.get(key) == value for key, value in expected.items())

    return {
        "samples": total,
        "parsed": parsed,
        "exact_matches": exact,
        "parse_rate": _ratio(parsed, total),
        "exact_match_accuracy": _ratio(exact, total),
        "field_accuracy": _ratio(field_correct, field_total),
        "sequence_accuracy": _ratio(
            sum(all(matches) for matches in example_matches.values()),
            len(example_matches),
        ),
        "by_structure": {
            structure: {
                "samples": counts[0],
                "exact_matches": counts[1],
                "exact_match_accuracy": _ratio(counts[1], counts[0]),
            }
            for structure, counts in sorted(structure_counts.items())
        },
    }


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def read_evaluations(source: str | Path) -> list[dict[str, Any]]:
    with Path(source).open(encoding="utf-8") as input_file:
        return [json.loads(line) for line in input_file if line.strip()]


def write_metrics(metrics: Mapping[str, Any], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
