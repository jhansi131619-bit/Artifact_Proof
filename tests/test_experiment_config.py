import json

import pytest

from artifactproof.synthetic.experiment import load_experiment_config, run_experiment
from artifactproof.synthetic.types import StructureKind


def test_load_and_run_experiment_config(tmp_path) -> None:
    output_dir = tmp_path / "run"
    config_path = tmp_path / "experiment.yaml"
    config_path.write_text(
        f"""name: test-run
output_dir: {output_dir.as_posix()}
structures: [heap, dsu]
generation:
  examples_per_structure: 1
  min_operations: 2
  max_operations: 2
  seed: 7
rendering:
  width: 400
  height: 300
model:
  enabled: false
"""
    )

    config = load_experiment_config(config_path)
    manifest = run_experiment(config)

    assert config.structures == (StructureKind.HEAP, StructureKind.DSU)
    assert manifest["programs"] == 2
    assert manifest["traces"] == 2
    assert manifest["frames"] == 6
    assert (output_dir / "programs.jsonl").exists()
    assert json.loads((output_dir / "run.json").read_text())["name"] == "test-run"


def test_config_rejects_enabled_model_without_endpoint(tmp_path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        "name: invalid\nstructures: [heap]\nmodel:\n  enabled: true\n  name: test\n"
    )

    with pytest.raises(ValueError, match="requires endpoint and name"):
        load_experiment_config(config_path)
