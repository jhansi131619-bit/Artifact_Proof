from artifactproof.synthetic import Operation, Program, StructureKind, execute_dsu, execute_heap
from artifactproof.synthetic.benchmark import summarize_traces


def test_benchmark_summary_checks_state_invariants() -> None:
    traces = [
        execute_heap(
            Program(
                example_id="heap-benchmark",
                structure=StructureKind.HEAP,
                operations=[Operation("push", (3,)), Operation("push", (1,))],
                metadata={"heap_order": "min"},
            )
        ),
        execute_dsu(
            Program(
                example_id="dsu-benchmark",
                structure=StructureKind.DSU,
                operations=[Operation("union", (0, 1))],
                metadata={"size": 3},
            )
        ),
    ]

    summary = summarize_traces(traces)

    assert summary["programs"] == 2
    assert summary["transitions"] == 3
    assert summary["states_checked"] == 5
    assert summary["all_invariants_valid"] is True
    assert summary["operations"] == {"push": 2, "union": 1}
