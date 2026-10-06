from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from .config import AblationSpec, ArtifactSpec, ConsumerSpec, RequirementSpec, TestSpec


def parse_requirement_file(path: str | Path) -> RequirementSpec:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Requirement file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Requirement file must contain a mapping: {file_path}")

    artifact_data = data.get("artifact") or {}
    consumer_data = data.get("consumer") or {}
    tests_data = data.get("tests") or {}
    ablation_data = data.get("ablation") or {}

    artifact = ArtifactSpec(
        file=str(artifact_data.get("file", "")),
        class_name=str(artifact_data.get("class", "")),
        functions=[str(item) for item in artifact_data.get("functions", [])],
    )
    consumer = ConsumerSpec(
        file=str(consumer_data.get("file", "")),
        class_name=str(consumer_data.get("class", "")),
    )
    tests = TestSpec(relevant=[str(item) for item in tests_data.get("relevant", [])])
    ablation = AblationSpec(
        target_function=str(ablation_data.get("target_function", "")),
        strategy=str(ablation_data.get("strategy", "constant_return")),
        return_value=ablation_data.get("return_value"),
    )

    return RequirementSpec(
        id=str(data.get("id", "")),
        description=str(data.get("description", "")),
        artifact=artifact,
        consumer=consumer,
        tests=tests,
        ablation=ablation,
    )
