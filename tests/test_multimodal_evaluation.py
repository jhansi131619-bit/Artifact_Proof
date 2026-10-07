import json
from pathlib import Path
from typing import Sequence

from artifactproof.synthetic import (
    MultimodalEvaluator,
    Operation,
    Program,
    StateRenderer,
    StructureKind,
    execute_heap,
)
from artifactproof.synthetic.evaluation import parse_prediction, write_evaluations


class QueueModel:
    name = "queue-model"

    def __init__(self, responses: list[str]) -> None:
        self.responses = iter(responses)
        self.calls: list[tuple[str, Sequence[Path]]] = []

    def predict(self, prompt: str, images: Sequence[Path]) -> str:
        self.calls.append((prompt, images))
        return next(self.responses)


def test_multimodal_evaluator_scores_each_transition(tmp_path) -> None:
    trace = execute_heap(
        Program(
            example_id="heap-eval",
            structure=StructureKind.HEAP,
            operations=[Operation("push", (5,)), Operation("push", (2,))],
            metadata={"heap_order": "min"},
        )
    )
    StateRenderer().render_trace(trace, tmp_path)
    model = QueueModel(
        [
            '{"values": [5], "result": null}',
            '```json\n{"values": [9], "result": null}\n```',
        ]
    )

    records = MultimodalEvaluator(model).evaluate_trace(trace, tmp_path)

    assert [record.exact_match for record in records] == [True, False]
    assert records[1].predicted == {"values": [9], "result": None}
    assert records[0].image.endswith("frame-001.png")
    assert len(model.calls) == 2

    output = write_evaluations(records, tmp_path / "evaluations.jsonl")
    lines = [json.loads(line) for line in output.read_text().splitlines()]
    assert lines[0]["sample_id"] == "heap-eval:1"


def test_prediction_parser_reports_non_json() -> None:
    predicted, error = parse_prediction("I cannot determine the state")

    assert predicted is None
    assert error and error.startswith("invalid JSON")
