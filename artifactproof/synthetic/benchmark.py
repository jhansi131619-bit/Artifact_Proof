"""Deterministic structural benchmark summaries for generated traces."""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from .types import StructureKind, Trace


def summarize_traces(traces: Iterable[Trace]) -> dict[str, Any]:
    items = list(traces)
    operation_counts: Counter[str] = Counter()
    structure_counts: Counter[str] = Counter()
    transitions = 0
    invariant_failures: list[str] = []

    for trace in items:
        trace.validate()
        structure_counts[trace.structure.value] += 1
        transitions += len(trace.operations)
        operation_counts.update(operation.name for operation in trace.operations)
        for step, state in enumerate(trace.states):
            if not _state_is_valid(trace.structure, state):
                invariant_failures.append(f"{trace.example_id}:{step}")

    return {
        "programs": len(items),
        "transitions": transitions,
        "average_operations": round(transitions / len(items), 3) if items else 0.0,
        "structures": dict(sorted(structure_counts.items())),
        "operations": dict(sorted(operation_counts.items())),
        "states_checked": sum(len(trace.states) for trace in items),
        "invariant_failures": invariant_failures,
        "all_invariants_valid": not invariant_failures,
    }


def _state_is_valid(structure: StructureKind, state: dict[str, Any]) -> bool:
    if structure is StructureKind.HEAP:
        values = state["values"]
        return all(
            values[(index - 1) // 2] <= values[index]
            for index in range(1, len(values))
        )
    parents = state["parents"]
    roots = sum(index == parent for index, parent in enumerate(parents))
    return (
        all(0 <= parent < len(parents) for parent in parents)
        and roots == state["components"]
    )
