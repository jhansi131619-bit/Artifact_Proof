"""Disjoint-set union (union-find) state transition generation."""

from __future__ import annotations

from typing import Any

from .types import Program, StructureKind, Trace


class DSUMachine:
    """Instrumented union-find using path compression and union by rank."""

    def __init__(self, size: int) -> None:
        if size < 1:
            raise ValueError("DSU size must be positive")
        self.parents = list(range(size))
        self.ranks = [0] * size
        self.components = size

    def snapshot(
        self,
        *,
        result: int | bool | None = None,
        touched: list[int] | None = None,
    ) -> dict[str, Any]:
        return {
            "parents": self.parents.copy(),
            "ranks": self.ranks.copy(),
            "components": self.components,
            "result": result,
            "touched": sorted(set(touched or [])),
        }

    def _check_index(self, item: int) -> None:
        if not 0 <= item < len(self.parents):
            raise IndexError(f"DSU index {item} is out of range")

    def _find_root(self, item: int, touched: list[int]) -> int:
        self._check_index(item)
        touched.append(item)
        root = item
        while root != self.parents[root]:
            root = self.parents[root]
            touched.append(root)
        while item != root:
            parent = self.parents[item]
            self.parents[item] = root
            item = parent
        return root

    def find(self, item: int) -> dict[str, Any]:
        touched: list[int] = []
        root = self._find_root(item, touched)
        return self.snapshot(result=root, touched=touched)

    def union(self, left: int, right: int) -> dict[str, Any]:
        touched: list[int] = []
        left_root = self._find_root(left, touched)
        right_root = self._find_root(right, touched)
        merged = left_root != right_root
        if merged:
            if self.ranks[left_root] < self.ranks[right_root]:
                left_root, right_root = right_root, left_root
            self.parents[right_root] = left_root
            if self.ranks[left_root] == self.ranks[right_root]:
                self.ranks[left_root] += 1
            self.components -= 1
            touched.extend([left_root, right_root])
        return self.snapshot(result=merged, touched=touched)

    def connected(self, left: int, right: int) -> dict[str, Any]:
        touched: list[int] = []
        connected = self._find_root(left, touched) == self._find_root(right, touched)
        return self.snapshot(result=connected, touched=touched)


def execute_dsu(program: Program) -> Trace:
    """Execute a DSU program and capture the state after each operation."""

    if program.structure is not StructureKind.DSU:
        raise ValueError("execute_dsu requires a DSU program")
    size = int(program.metadata.get("size", 0))
    machine = DSUMachine(size)
    states = [machine.snapshot()]

    for operation in program.operations:
        if operation.name == "union" and len(operation.arguments) == 2:
            state = machine.union(*operation.arguments)
        elif operation.name == "connected" and len(operation.arguments) == 2:
            state = machine.connected(*operation.arguments)
        elif operation.name == "find" and len(operation.arguments) == 1:
            state = machine.find(operation.arguments[0])
        else:
            raise ValueError(f"unsupported DSU operation: {operation.to_code()}")
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
