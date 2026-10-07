"""JSON Lines persistence for generated programs and executed traces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, TypeVar

from .types import Program, Trace

Record = TypeVar("Record", Program, Trace)


def write_jsonl(records: Iterable[Program | Trace], destination: str | Path) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
    return path


def read_programs(source: str | Path) -> Iterator[Program]:
    with Path(source).open(encoding="utf-8") as input_file:
        for line in input_file:
            if line.strip():
                yield Program.from_dict(json.loads(line))


def read_traces(source: str | Path) -> Iterator[Trace]:
    with Path(source).open(encoding="utf-8") as input_file:
        for line in input_file:
            if line.strip():
                yield Trace.from_dict(json.loads(line))
