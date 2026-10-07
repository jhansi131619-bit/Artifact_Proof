"""Command-line interface for the synthetic benchmark pipeline."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from .dataset import write_jsonl
from .generator import GeneratorConfig, SyntheticProgramGenerator
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
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
