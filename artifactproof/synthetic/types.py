"""Core, JSON-serializable types used by the synthetic benchmark."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class StructureKind(StrEnum):
    """Data structures supported by the benchmark."""

    HEAP = "heap"
    DSU = "dsu"


@dataclass(frozen=True, slots=True)
class Operation:
    """One operation in a generated data-structure program."""

    name: str
    arguments: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "arguments": list(self.arguments)}

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Operation:
        return cls(
            name=str(value["name"]),
            arguments=tuple(int(item) for item in value.get("arguments", [])),
        )


@dataclass(slots=True)
class Trace:
    """A complete state-transition trace for a generated program."""

    example_id: str
    structure: StructureKind
    operations: list[Operation]
    states: list[dict[str, Any]]
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if len(self.states) != len(self.operations) + 1:
            raise ValueError("a trace must contain the initial state and one state per operation")
        if not self.example_id:
            raise ValueError("example_id must not be empty")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return {
            "example_id": self.example_id,
            "structure": self.structure.value,
            "operations": [operation.to_dict() for operation in self.operations],
            "states": self.states,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Trace:
        trace = cls(
            example_id=str(value["example_id"]),
            structure=StructureKind(value["structure"]),
            operations=[Operation.from_dict(item) for item in value["operations"]],
            states=list(value["states"]),
            metadata=dict(value.get("metadata", {})),
        )
        trace.validate()
        return trace
