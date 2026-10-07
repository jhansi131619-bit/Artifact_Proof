"""Command-line interface for the synthetic benchmark pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .dataset import read_programs, read_traces, write_jsonl
from .generator import GeneratorConfig, SyntheticProgramGenerator
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
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
