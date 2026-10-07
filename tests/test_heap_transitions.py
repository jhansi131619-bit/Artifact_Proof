import heapq

import pytest

from artifactproof.synthetic import Operation, Program, StructureKind, execute_heap


def heap_program(*operations: Operation) -> Program:
    return Program(
        example_id="heap-test",
        structure=StructureKind.HEAP,
        operations=list(operations),
        metadata={"heap_order": "min"},
    )


def test_heap_trace_captures_push_and_pop_states() -> None:
    program = heap_program(
        Operation("push", (8,)),
        Operation("push", (3,)),
        Operation("push", (5,)),
        Operation("push", (1,)),
        Operation("pop"),
    )

    trace = execute_heap(program)

    assert len(trace.states) == 6
    assert trace.states[4]["values"] == [1, 3, 5, 8]
    assert trace.states[4]["touched"] == [0, 1, 3]
    assert trace.states[5]["result"] == 1
    assert trace.states[5]["values"] == [3, 8, 5]


def test_every_heap_snapshot_preserves_heap_property() -> None:
    operations = [Operation("push", (value,)) for value in [9, 4, 7, 1, 3, 2]]
    operations.extend([Operation("pop"), Operation("pop")])

    trace = execute_heap(heap_program(*operations))

    for state in trace.states:
        values = state["values"]
        assert all(values[(index - 1) // 2] <= values[index] for index in range(1, len(values)))


def test_heap_matches_standard_library_results() -> None:
    values = [11, 2, 8, 2, 6]
    operations = [Operation("push", (value,)) for value in values]
    operations.extend([Operation("pop") for _ in values])
    trace = execute_heap(heap_program(*operations))

    expected = values.copy()
    heapq.heapify(expected)
    popped = [heapq.heappop(expected) for _ in values]
    actual = [state["result"] for state in trace.states if state["result"] is not None]
    assert actual == popped


def test_heap_rejects_invalid_operations() -> None:
    with pytest.raises(IndexError, match="empty heap"):
        execute_heap(heap_program(Operation("pop")))

    with pytest.raises(ValueError, match="unsupported heap operation"):
        execute_heap(heap_program(Operation("remove", (2,))))
