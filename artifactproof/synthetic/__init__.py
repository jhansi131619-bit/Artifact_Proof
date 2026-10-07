"""Synthetic data-structure traces for multimodal evaluation."""

from .types import Operation, Program, StructureKind, Trace
from .heap import HeapMachine, execute_heap
from .transitions import execute_program

__all__ = [
    "HeapMachine",
    "Operation",
    "Program",
    "StructureKind",
    "Trace",
    "execute_heap",
    "execute_program",
]
