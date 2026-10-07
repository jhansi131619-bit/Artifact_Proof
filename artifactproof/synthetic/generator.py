"""Deterministic generators for synthetic data-structure programs."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable

from .types import Operation, Program, StructureKind


@dataclass(frozen=True, slots=True)
class GeneratorConfig:
    examples_per_structure: int = 100
    min_operations: int = 3
    max_operations: int = 10
    max_value: int = 99
    dsu_min_size: int = 4
    dsu_max_size: int = 10
    seed: int = 0

    def validate(self) -> None:
        if self.examples_per_structure < 1:
            raise ValueError("examples_per_structure must be positive")
        if not 1 <= self.min_operations <= self.max_operations:
            raise ValueError("operation limits must be positive and ordered")
        if self.max_value < 0:
            raise ValueError("max_value must be non-negative")
        if not 2 <= self.dsu_min_size <= self.dsu_max_size:
            raise ValueError("DSU size limits must be at least two and ordered")


class SyntheticProgramGenerator:
    """Generate reproducible operation programs without executing them."""

    def __init__(self, config: GeneratorConfig | None = None) -> None:
        self.config = config or GeneratorConfig()
        self.config.validate()
        self._random = Random(self.config.seed)

    def generate(
        self,
        structures: Iterable[StructureKind] = tuple(StructureKind),
    ) -> list[Program]:
        programs: list[Program] = []
        for structure in structures:
            for index in range(self.config.examples_per_structure):
                length = self._random.randint(
                    self.config.min_operations,
                    self.config.max_operations,
                )
                if structure is StructureKind.HEAP:
                    operations = self._heap_operations(length)
                    metadata = {"heap_order": "min"}
                elif structure is StructureKind.DSU:
                    size = self._random.randint(
                        self.config.dsu_min_size,
                        self.config.dsu_max_size,
                    )
                    operations = self._dsu_operations(length, size)
                    metadata = {"size": size}
                else:  # pragma: no cover - the enum prevents this in normal use
                    raise ValueError(f"unsupported structure: {structure}")
                programs.append(
                    Program(
                        example_id=f"{structure.value}-{index:05d}",
                        structure=structure,
                        operations=operations,
                        metadata={**metadata, "seed": self.config.seed},
                    )
                )
        return programs

    def _heap_operations(self, length: int) -> list[Operation]:
        operations: list[Operation] = []
        heap_size = 0
        for _ in range(length):
            if heap_size == 0 or self._random.random() < 0.68:
                operations.append(
                    Operation("push", (self._random.randint(0, self.config.max_value),))
                )
                heap_size += 1
            else:
                operations.append(Operation("pop"))
                heap_size -= 1
        return operations

    def _dsu_operations(self, length: int, size: int) -> list[Operation]:
        operations: list[Operation] = []
        choices = ("union", "connected", "find")
        weights = (0.58, 0.27, 0.15)
        for _ in range(length):
            name = self._random.choices(choices, weights=weights, k=1)[0]
            left = self._random.randrange(size)
            if name == "find":
                operations.append(Operation(name, (left,)))
            else:
                right = self._random.randrange(size)
                operations.append(Operation(name, (left, right)))
        return operations
