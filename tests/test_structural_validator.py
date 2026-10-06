from pathlib import Path

from artifactproof.structural_validator import StructuralValidator


def test_structural_validator_identifies_required_changes():
    repo = Path("benchmark/discount_engine/correct")
    validator = StructuralValidator.from_requirement_file("benchmark/discount_engine/requirement.yaml")
    result = validator.validate(repo)
    assert result["artifact_file_exists"] is True
    assert result["class_exists"] is True
    assert result["function_exists"] is True
    assert result["consumer_imports_artifact"] is True
    assert result["consumer_references_artifact"] is True
    assert result["status"] == "PASS"
