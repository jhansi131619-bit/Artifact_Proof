"""Min-heap state transition generation."""

from __future__ import annotations

from typing import Any

from .types import Program, StructureKind, Trace


class HeapMachine:
    """A small instrumented min-heap that exposes deterministic snapshots."""

    def __init__(self) -> None:
        self.values: list[int] = []

    def snapshot(
        self,
        *,
        result: int | None = None,
        touched: list[int] | None = None,
    ) -> dict[str, Any]:
        return {
            "values": self.values.copy(),
            "result": result,
            "touched": sorted(set(touched or [])),
        }

    def push(self, value: int) -> dict[str, Any]:
        self.values.append(value)
        current = len(self.values) - 1
        touched = [current]
        while current:
            parent = (current - 1) // 2
            touched.append(parent)
            if self.values[parent] <= self.values[current]:
                break
            self.values[parent], self.values[current] = (
                self.values[current],
                self.values[parent],
            )
            current = parent
        return self.snapshot(touched=touched)

    def pop(self) -> dict[str, Any]:
        if not self.values:
            raise IndexError("cannot pop from an empty heap")
        result = self.values[0]
        last = self.values.pop()
        touched = [0]
        if self.values:
            self.values[0] = last
            current = 0
            while True:
                left = 2 * current + 1
                right = left + 1
                smallest = current
                if left < len(self.values) and self.values[left] < self.values[smallest]:
                    smallest = left
                if right < len(self.values) and self.values[right] < self.values[smallest]:
                    smallest = right
                if smallest == current:
                    break
                touched.extend([current, smallest])
                self.values[current], self.values[smallest] = (
                    self.values[smallest],
                    self.values[current],
                )
                current = smallest
        return self.snapshot(result=result, touched=touched)

    def peek(self) -> dict[str, Any]:
        if not self.values:
            raise IndexError("cannot peek at an empty heap")
        return self.snapshot(result=self.values[0], touched=[0])


def execute_heap(program: Program) -> Trace:
    """Execute a heap program and capture the state after each operation."""

    if program.structure is not StructureKind.HEAP:
        raise ValueError("execute_heap requires a heap program")
    if program.metadata.get("heap_order", "min") != "min":
        raise ValueError("only min-heaps are supported")

    machine = HeapMachine()
    states = [machine.snapshot()]
    for operation in program.operations:
        if operation.name == "push" and len(operation.arguments) == 1:
            state = machine.push(operation.arguments[0])
        elif operation.name == "pop" and not operation.arguments:
            state = machine.pop()
        elif operation.name == "peek" and not operation.arguments:
            state = machine.peek()
        else:
            raise ValueError(f"unsupported heap operation: {operation.to_code()}")
        states.append(state)

    trace = Trace(
        example_id=program.example_id,
        structure=program.structure,
        operations=program.operations,
        states=states,
        metadata=program.metadata,
    )
    trace.validate()
    return trace
