from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List

from .requirement_parser import parse_requirement_file


class StructuralValidator:
    def __init__(self, requirement_path: str | Path):
        self.requirement = parse_requirement_file(requirement_path)

    @classmethod
    def from_requirement_file(cls, requirement_path: str | Path) -> "StructuralValidator":
        return cls(requirement_path)

    def validate(self, repo_root: str | Path) -> Dict[str, Any]:
        root = Path(repo_root)
        artifact_file = root / self.requirement.artifact.file
        consumer_file = root / self.requirement.consumer.file

        evidence: Dict[str, Any] = {
            "artifact_file_exists": artifact_file.exists(),
            "class_exists": False,
            "function_exists": False,
            "consumer_exists": consumer_file.exists(),
            "consumer_imports_artifact": False,
            "consumer_references_artifact": False,
            "status": "FAIL",
        }

        if artifact_file.exists():
            try:
                tree = ast.parse(artifact_file.read_text(encoding="utf-8"), filename=str(artifact_file))
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == self.requirement.artifact.class_name:
                        evidence["class_exists"] = True
                    if isinstance(node, ast.FunctionDef) and node.name in self.requirement.artifact.functions:
                        evidence["function_exists"] = True
            except SyntaxError:
                evidence["class_exists"] = False
                evidence["function_exists"] = False

        if consumer_file.exists():
            try:
                tree = ast.parse(consumer_file.read_text(encoding="utf-8"), filename=str(consumer_file))
                imported_names = set()
                referenced_names = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_names.add(node.module)
                        for alias in node.names:
                            imported_names.add(alias.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_names.add(alias.name)
                    elif isinstance(node, ast.Name):
                        referenced_names.add(node.id)

                artifact_module = self.requirement.artifact.file.replace(".py", "")
                if artifact_module in imported_names or f"from {artifact_module}" in str(tree):
                    evidence["consumer_imports_artifact"] = True
                if self.requirement.artifact.class_name in referenced_names or artifact_module in referenced_names:
                    evidence["consumer_references_artifact"] = True
                if self.requirement.consumer.class_name:
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name == self.requirement.consumer.class_name:
                            evidence["consumer_references_artifact"] = True
            except SyntaxError:
                pass

        if all(
            [
                evidence["artifact_file_exists"],
                evidence["class_exists"],
                evidence["function_exists"],
                evidence["consumer_exists"],
            ]
        ):
            evidence["status"] = "PASS"

        explanation = self._explain(evidence)
        evidence["explanation"] = explanation
        return evidence

    def _explain(self, evidence: Dict[str, Any]) -> str:
        lines = [
            "Structural validation for required artifact and consumer.",
            f"Artifact file exists: {'YES' if evidence['artifact_file_exists'] else 'NO'}",
            f"Artifact class exists: {'YES' if evidence['class_exists'] else 'NO'}",
            f"Artifact function exists: {'YES' if evidence['function_exists'] else 'NO'}",
            f"Consumer file exists: {'YES' if evidence['consumer_exists'] else 'NO'}",
            f"Consumer imports artifact: {'YES' if evidence['consumer_imports_artifact'] else 'NO'}",
            f"Consumer references artifact: {'YES' if evidence['consumer_references_artifact'] else 'NO'}",
            f"Status: {evidence['status']}",
        ]
        return "\n".join(lines)
