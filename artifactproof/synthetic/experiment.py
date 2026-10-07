"""Configuration and orchestration for reproducible synthetic experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .dataset import write_jsonl
from .evaluation import MultimodalEvaluator, write_evaluations
from .generator import GeneratorConfig, SyntheticProgramGenerator
from .metrics import summarize_evaluations, write_metrics
from .models import HTTPVisionModel
from .render import RenderTheme, StateRenderer
from .transitions import execute_program
from .types import StructureKind


@dataclass(frozen=True, slots=True)
class ModelConfig:
    enabled: bool = False
    endpoint: str = ""
    name: str = ""
    api_key_env: str = "ARTIFACTPROOF_MODEL_API_KEY"
    timeout_seconds: float = 60.0

    def validate(self) -> None:
        if self.enabled and (not self.endpoint or not self.name):
            raise ValueError("enabled model config requires endpoint and name")


@dataclass(frozen=True, slots=True)
class ExperimentConfig:
    name: str
    output_dir: Path
    structures: tuple[StructureKind, ...]
    generation: GeneratorConfig
    rendering: RenderTheme
    model: ModelConfig

    def validate(self) -> None:
        if not self.name.strip():
            raise ValueError("experiment name must not be empty")
        if not self.structures:
            raise ValueError("at least one structure must be configured")
        self.generation.validate()
        self.model.validate()


def load_experiment_config(source: str | Path) -> ExperimentConfig:
    path = Path(source)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    generation = raw.get("generation", {})
    rendering = raw.get("rendering", {})
    model = raw.get("model", {})
    config = ExperimentConfig(
        name=str(raw.get("name", "")),
        output_dir=Path(raw.get("output_dir", "results/synthetic")),
        structures=tuple(StructureKind(value) for value in raw.get("structures", [])),
        generation=GeneratorConfig(
            examples_per_structure=int(generation.get("examples_per_structure", 100)),
            min_operations=int(generation.get("min_operations", 3)),
            max_operations=int(generation.get("max_operations", 10)),
            max_value=int(generation.get("max_value", 99)),
            dsu_min_size=int(generation.get("dsu_min_size", 4)),
            dsu_max_size=int(generation.get("dsu_max_size", 10)),
            seed=int(generation.get("seed", 0)),
        ),
        rendering=RenderTheme(
            **{key: value for key, value in rendering.items() if key in RenderTheme.__dataclass_fields__}
        ),
        model=ModelConfig(
            enabled=bool(model.get("enabled", False)),
            endpoint=str(model.get("endpoint", "")),
            name=str(model.get("name", "")),
            api_key_env=str(model.get("api_key_env", "ARTIFACTPROOF_MODEL_API_KEY")),
            timeout_seconds=float(model.get("timeout_seconds", 60.0)),
        ),
    )
    config.validate()
    return config


def run_experiment(config: ExperimentConfig) -> dict[str, Any]:
    """Materialize configured artifacts and return a compact run manifest."""

    config.validate()
    output_dir = config.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    programs = SyntheticProgramGenerator(config.generation).generate(config.structures)
    traces = [execute_program(program) for program in programs]
    programs_path = write_jsonl(programs, output_dir / "programs.jsonl")
    traces_path = write_jsonl(traces, output_dir / "traces.jsonl")
    renderer = StateRenderer(config.rendering)
    frames = [
        frame
        for trace in traces
        for frame in renderer.render_trace(trace, output_dir / "images")
    ]
    manifest: dict[str, Any] = {
        "name": config.name,
        "programs": len(programs),
        "traces": len(traces),
        "frames": len(frames),
        "programs_path": str(programs_path),
        "traces_path": str(traces_path),
        "images_path": str(output_dir / "images"),
        "evaluation_enabled": config.model.enabled,
    }
    if config.model.enabled:
        adapter = HTTPVisionModel(
            endpoint=config.model.endpoint,
            model=config.model.name,
            api_key_env=config.model.api_key_env,
            timeout_seconds=config.model.timeout_seconds,
        )
        records = MultimodalEvaluator(adapter).evaluate(traces, output_dir / "images")
        evaluations_path = write_evaluations(records, output_dir / "evaluations.jsonl")
        metrics_path = write_metrics(
            summarize_evaluations(records),
            output_dir / "metrics.json",
        )
        manifest.update(
            evaluations_path=str(evaluations_path),
            metrics_path=str(metrics_path),
        )
    write_metrics(manifest, output_dir / "run.json")
    return manifest
