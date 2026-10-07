"""Command-line interface for the synthetic benchmark pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .dataset import read_programs, read_traces, write_jsonl
from .generator import GeneratorConfig, SyntheticProgramGenerator
from .evaluation import MultimodalEvaluator, write_evaluations
from .models import HTTPVisionModel
from .render import StateRenderer
from .transitions import execute_program
from .types import StructureKind


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="artifactproof-synthetic")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate", help="generate operation programs")
    generate.add_argument("--output", required=True)
    generate.add_argument("--examples", type=int, default=100)
    generate.add_argument("--min-operations", type=int, default=3)
    generate.add_argument("--max-operations", type=int, default=10)
    generate.add_argument("--seed", type=int, default=0)
    generate.add_argument(
        "--structure",
        action="append",
        choices=[kind.value for kind in StructureKind],
    )
    execute = subparsers.add_parser("execute", help="execute programs into traces")
    execute.add_argument("--input", required=True)
    execute.add_argument("--output", required=True)
    render = subparsers.add_parser("render", help="render trace frames as PNG files")
    render.add_argument("--input", required=True)
    render.add_argument("--output-dir", required=True)
    evaluate = subparsers.add_parser("evaluate", help="evaluate rendered traces with a model")
    evaluate.add_argument("--input", required=True, help="trace JSONL file")
    evaluate.add_argument("--images", required=True, help="rendered image root")
    evaluate.add_argument("--output", required=True, help="evaluation JSONL file")
    evaluate.add_argument("--endpoint", required=True)
    evaluate.add_argument("--model", required=True)
    evaluate.add_argument("--api-key-env", default="ARTIFACTPROOF_MODEL_API_KEY")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    if arguments.command == "generate":
        config = GeneratorConfig(
            examples_per_structure=arguments.examples,
            min_operations=arguments.min_operations,
            max_operations=arguments.max_operations,
            seed=arguments.seed,
        )
        structures = (
            [StructureKind(item) for item in arguments.structure]
            if arguments.structure
            else list(StructureKind)
        )
        programs = SyntheticProgramGenerator(config).generate(structures)
        write_jsonl(programs, arguments.output)
        print(f"wrote {len(programs)} programs to {arguments.output}")
        return 0
    if arguments.command == "execute":
        traces = [execute_program(program) for program in read_programs(arguments.input)]
        write_jsonl(traces, arguments.output)
        print(f"wrote {len(traces)} traces to {arguments.output}")
        return 0
    if arguments.command == "render":
        renderer = StateRenderer()
        count = 0
        for trace in read_traces(arguments.input):
            count += len(renderer.render_trace(trace, arguments.output_dir))
        print(f"wrote {count} frames to {arguments.output_dir}")
        return 0
    if arguments.command == "evaluate":
        model = HTTPVisionModel(
            endpoint=arguments.endpoint,
            model=arguments.model,
            api_key_env=arguments.api_key_env,
        )
        evaluator = MultimodalEvaluator(model)
        records = evaluator.evaluate(read_traces(arguments.input), arguments.images)
        write_evaluations(records, arguments.output)
        print(f"wrote {len(records)} evaluations to {arguments.output}")
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
