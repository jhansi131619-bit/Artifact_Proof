"""Generate the configured corpus and record deterministic benchmark statistics."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from artifactproof.synthetic.benchmark import summarize_traces
from artifactproof.synthetic.experiment import load_experiment_config
from artifactproof.synthetic.generator import SyntheticProgramGenerator
from artifactproof.synthetic.transitions import execute_program


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="experiments/synthetic_benchmark.yaml")
    parser.add_argument("--output", default="results/synthetic_benchmark_summary.json")
    arguments = parser.parse_args()

    config = load_experiment_config(arguments.config)
    programs = SyntheticProgramGenerator(config.generation).generate(config.structures)
    summary = summarize_traces(execute_program(program) for program in programs)
    summary.update(
        experiment=config.name,
        seed=config.generation.seed,
        examples_per_structure=config.generation.examples_per_structure,
    )
    output = Path(arguments.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote benchmark summary to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
