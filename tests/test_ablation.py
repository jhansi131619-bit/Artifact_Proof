import ast
from pathlib import Path

from artifactproof.ablation import AblationEngine


def test_ablation_preserves_syntax_and_writes_mutated_repo():
    result = AblationEngine.mutate_repository(
        "benchmark/discount_engine/correct",
        "discount_engine.py",
        "calculate_discount",
        strategy="constant_return",
        return_value=None,
    )

    mutated_file = Path(result.mutated_repo) / "discount_engine.py"
    assert mutated_file.exists()
    assert "return None" in mutated_file.read_text(encoding="utf-8")
    ast.parse(mutated_file.read_text(encoding="utf-8"), filename=str(mutated_file))
