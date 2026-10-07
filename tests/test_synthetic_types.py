import pytest

from artifactproof.synthetic import Operation, StructureKind, Trace


def test_trace_round_trip() -> None:
    trace = Trace(
        example_id="heap-0001",
        structure=StructureKind.HEAP,
        operations=[Operation("push", (4,))],
        states=[{"values": []}, {"values": [4]}],
        metadata={"seed": 7},
    )

    assert Trace.from_dict(trace.to_dict()) == trace


def test_trace_rejects_missing_state() -> None:
    trace = Trace(
        example_id="bad",
        structure=StructureKind.DSU,
        operations=[Operation("union", (0, 1))],
        states=[{"parents": [0, 1]}],
    )

    with pytest.raises(ValueError, match="one state per operation"):
        trace.validate()
