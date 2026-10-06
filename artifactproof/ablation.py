from __future__ import annotations

import ast
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class AblationResult:
    source_repo: str
    mutated_repo: str
    target_function: str
    strategy: str
    mutation_log: list[str]
    status: str


class AblationEngine:
    @staticmethod
    def copy_repository(repo_root: str | Path) -> Path:
        src = Path(repo_root)
        temp_dir = Path(tempfile.mkdtemp(prefix="artifactproof_ablation_"))
        destination = temp_dir / src.name
        shutil.copytree(src, destination)
        return destination

    @staticmethod
    def _rewrite_function(source: str, function_name: str, strategy: str = "constant_return", return_value: Any = None) -> tuple[str, list[str]]:
        tree = ast.parse(source)
        target = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                target = node
                break
        if target is None:
            raise ValueError(f"Function not found: {function_name}")

        value = return_value if return_value is not None else None
        constant = AblationEngine._constant_literal(value, strategy)
        replacement_expr = ast.parse(f"return {constant}").body[0]
        target.body = [replacement_expr]
        fixed_source = ast.unparse(tree)
        return fixed_source + "\n", [f"Replaced function {function_name} with constant return {constant}"]

    @staticmethod
    def _constant_literal(return_value: Any, strategy: str) -> str:
        if strategy == "return_none":
            return "None"
        if strategy == "return_zero":
            return "0"
        if strategy == "return_false":
            return "False"
        if strategy == "raise_exception":
            return "_raise_exception()"
        if strategy == "constant_return":
            if return_value is None:
                return "None"
            if isinstance(return_value, bool):
                return "True" if return_value else "False"
            if isinstance(return_value, (int, float)):
                return str(return_value)
            return repr(return_value)
        return "None"

    @classmethod
    def mutate_repository(cls, repo_root: str | Path, artifact_path: str, function_name: str, strategy: str = "constant_return", return_value: Any = None) -> AblationResult:
        src = Path(repo_root)
        target_path = src / artifact_path
        if not target_path.exists():
            raise FileNotFoundError(f"Artifact not found for ablation: {target_path}")

        source = target_path.read_text(encoding="utf-8")
        updated_source, mutation_log = cls._rewrite_function(source, function_name, strategy=strategy, return_value=return_value)
        clone_root = cls.copy_repository(src)
        clone_target = clone_root / artifact_path
        clone_target.write_text(updated_source, encoding="utf-8")
        return AblationResult(
            source_repo=str(src),
            mutated_repo=str(clone_root),
            target_function=function_name,
            strategy=strategy,
            mutation_log=mutation_log,
            status="OK",
        )
