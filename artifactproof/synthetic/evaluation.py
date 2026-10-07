"""Multimodal state-prediction evaluation over rendered traces."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .models import VisionModel
from .types import Operation, StructureKind, Trace


@dataclass(slots=True)
class EvaluationRecord:
    sample_id: str
    example_id: str
    step: int
    structure: str
    operation: dict[str, Any]
    image: str
    model: str
    prompt: str
    raw_response: str
    expected: dict[str, Any]
    predicted: dict[str, Any] | None
    parse_error: str | None
    exact_match: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MultimodalEvaluator:
    """Ask a vision model to recover each post-operation state from a frame."""

    def __init__(self, model: VisionModel) -> None:
        self.model = model

    def evaluate_trace(self, trace: Trace, images_root: str | Path) -> list[EvaluationRecord]:
        trace.validate()
        records: list[EvaluationRecord] = []
        image_directory = Path(images_root) / trace.example_id
        for step, (operation, state) in enumerate(
            zip(trace.operations, trace.states[1:], strict=True),
            start=1,
        ):
            image = image_directory / f"frame-{step:03d}.png"
            if not image.is_file():
                raise FileNotFoundError(f"missing rendered frame: {image}")
            expected = expected_state(trace.structure, state)
            prompt = build_prompt(trace.structure, operation)
            raw_response = self.model.predict(prompt, [image])
            predicted, parse_error = parse_prediction(raw_response)
            records.append(
                EvaluationRecord(
                    sample_id=f"{trace.example_id}:{step}",
                    example_id=trace.example_id,
                    step=step,
                    structure=trace.structure.value,
                    operation=operation.to_dict(),
                    image=str(image),
                    model=self.model.name,
                    prompt=prompt,
                    raw_response=raw_response,
                    expected=expected,
                    predicted=predicted,
                    parse_error=parse_error,
                    exact_match=predicted == expected,
                )
            )
        return records

    def evaluate(
        self,
        traces: Iterable[Trace],
        images_root: str | Path,
    ) -> list[EvaluationRecord]:
        return [
            record
            for trace in traces
            for record in self.evaluate_trace(trace, images_root)
        ]


def build_prompt(structure: StructureKind, operation: Operation) -> str:
    fields = "values, result" if structure is StructureKind.HEAP else "parents, components, result"
    return (
        f"Inspect this {structure.value} state after {operation.to_code()}. "
        f"Return only a JSON object with these fields: {fields}."
    )


def expected_state(structure: StructureKind, state: dict[str, Any]) -> dict[str, Any]:
    if structure is StructureKind.HEAP:
        return {"values": state["values"], "result": state.get("result")}
    return {
        "parents": state["parents"],
        "components": state["components"],
        "result": state.get("result"),
    }


def parse_prediction(raw_response: str) -> tuple[dict[str, Any] | None, str | None]:
    candidate = raw_response.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError as error:
        return None, f"invalid JSON: {error.msg}"
    if not isinstance(parsed, dict):
        return None, "prediction must be a JSON object"
    return parsed, None


def write_evaluations(
    records: Iterable[EvaluationRecord],
    destination: str | Path,
) -> Path:
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as output:
        for record in records:
            output.write(json.dumps(record.to_dict(), sort_keys=True) + "\n")
    return path
