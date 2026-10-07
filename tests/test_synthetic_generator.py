import json

from artifactproof.synthetic import Program, StructureKind
from artifactproof.synthetic.cli import main
from artifactproof.synthetic.dataset import read_programs, write_jsonl
from artifactproof.synthetic.generator import GeneratorConfig, SyntheticProgramGenerator


def test_program_generation_is_reproducible() -> None:
    config = GeneratorConfig(examples_per_structure=3, seed=42)

    first = SyntheticProgramGenerator(config).generate()
    second = SyntheticProgramGenerator(config).generate()

    assert [item.to_dict() for item in first] == [item.to_dict() for item in second]
    assert {item.structure for item in first} == set(StructureKind)


def test_generated_operations_are_well_formed() -> None:
    config = GeneratorConfig(examples_per_structure=25, seed=9)
    programs = SyntheticProgramGenerator(config).generate()

    for program in programs:
        if program.structure is StructureKind.HEAP:
            size = 0
            for operation in program.operations:
                size += 1 if operation.name == "push" else -1
                assert size >= 0
        else:
            size = program.metadata["size"]
            assert all(0 <= value < size for op in program.operations for value in op.arguments)


def test_jsonl_round_trip_and_cli(tmp_path) -> None:
    path = tmp_path / "programs.jsonl"
    assert main(["generate", "--output", str(path), "--examples", "2", "--seed", "3"]) == 0

    programs = list(read_programs(path))
    assert len(programs) == 4
    assert all(isinstance(item, Program) for item in programs)
    assert "code" in json.loads(path.read_text().splitlines()[0])

    copied = tmp_path / "copy.jsonl"
    write_jsonl(programs, copied)
    assert list(read_programs(copied)) == programs
