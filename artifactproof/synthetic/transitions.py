"""Dispatch generated programs to data-structure state machines."""

from __future__ import annotations

from .heap import execute_heap
from .types import Program, StructureKind, Trace


def execute_program(program: Program) -> Trace:
    if program.structure is StructureKind.HEAP:
        return execute_heap(program)
    raise ValueError(f"no transition generator registered for {program.structure.value}")
