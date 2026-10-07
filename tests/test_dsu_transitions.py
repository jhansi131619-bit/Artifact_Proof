import pytest

from artifactproof.synthetic import Operation, Program, StructureKind, execute_dsu


def dsu_program(size: int, *operations: Operation) -> Program:
    return Program(
        example_id="dsu-test",
        structure=StructureKind.DSU,
        operations=list(operations),
        metadata={"size": size},
    )


def test_dsu_trace_captures_unions_and_queries() -> None:
    trace = execute_dsu(
        dsu_program(
            5,
            Operation("union", (0, 1)),
            Operation("union", (2, 3)),
            Operation("connected", (0, 3)),
            Operation("union", (1, 3)),
            Operation("connected", (0, 2)),
        )
    )

    assert len(trace.states) == 6
    assert trace.states[1]["result"] is True
    assert trace.states[3]["result"] is False
    assert trace.states[4]["components"] == 2
    assert trace.states[5]["result"] is True


def test_dsu_redundant_union_does_not_change_component_count() -> None:
    trace = execute_dsu(
        dsu_program(
            3,
            Operation("union", (0, 1)),
            Operation("union", (1, 0)),
        )
    )

    assert trace.states[1]["components"] == 2
    assert trace.states[2]["components"] == 2
    assert trace.states[2]["result"] is False


def test_find_compresses_paths_and_returns_root() -> None:
    trace = execute_dsu(
        dsu_program(
            8,
            Operation("union", (0, 1)),
            Operation("union", (2, 3)),
            Operation("union", (0, 2)),
            Operation("union", (4, 5)),
            Operation("union", (6, 7)),
            Operation("union", (4, 6)),
            Operation("union", (0, 4)),
            Operation("find", (7,)),
        )
    )

    final = trace.states[-1]
    assert final["result"] == 0
    assert final["parents"][7] == 0
    assert {0, 4, 6, 7}.issubset(final["touched"])


def test_dsu_rejects_invalid_input() -> None:
    with pytest.raises(ValueError, match="size must be positive"):
        execute_dsu(dsu_program(0))

    with pytest.raises(IndexError, match="out of range"):
        execute_dsu(dsu_program(2, Operation("find", (2,))))

    with pytest.raises(ValueError, match="unsupported DSU operation"):
        execute_dsu(dsu_program(2, Operation("push", (1,))))
