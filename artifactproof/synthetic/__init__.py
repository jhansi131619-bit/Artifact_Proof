"""Synthetic data-structure traces for multimodal evaluation."""

from .types import Operation, Program, StructureKind, Trace
from .dsu import DSUMachine, execute_dsu
from .heap import HeapMachine, execute_heap
from .transitions import execute_program

__all__ = [
    "DSUMachine",
    "HeapMachine",
    "Operation",
    "Program",
    "StructureKind",
    "Trace",
    "execute_dsu",
    "execute_heap",
    "execute_program",
]
