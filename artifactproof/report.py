from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class ReportBuilder:
    @staticmethod
    def render_text(requirement: Any, structural: Dict[str, Any], baseline: Any, post: Any, causal: Any) -> str:
        lines = [
            "Requirement:",
            requirement.description,
            "",
            f"Requested artifact: {requirement.artifact.file}::{requirement.artifact.class_name}",
            "",
            "FUNCTIONAL VALIDATION",
            f"{baseline.passed} / {baseline.total_tests} tests passed",
            f"Status: {'PASS' if baseline.failed == 0 else 'FAIL'}",
            "",
            "STRUCTURAL VALIDATION",
            f"Artifact file exists: {'YES' if structural['artifact_file_exists'] else 'NO'}",
            f"{requirement.artifact.class_name} exists: {'YES' if structural['class_exists'] else 'NO'}",
            f"{requirement.artifact.functions[0]} exists: {'YES' if structural['function_exists'] else 'NO'}",
            f"Consumer imports artifact: {'YES' if structural['consumer_imports_artifact'] else 'NO'}",
            f"Consumer references artifact: {'YES' if structural['consumer_references_artifact'] else 'NO'}",
            f"Status: {structural['status']}",
            "",
            "CAUSAL VALIDATION",
            f"Ablation: {requirement.artifact.file}::{requirement.artifact.class_name}.{requirement.ablation.target_function} neutralized",
            f"Relevant tests before: {causal.relevant_tests_before} / {baseline.total_tests} passed",
            f"Relevant tests after: {post.passed} / {post.total_tests} passed",
            f"Artifact Causal Score: {causal.artifact_causal_score:.2f}",
            "",
            "FINAL VERDICT:",
            causal.status,
            "",
            "Reason:",
            causal.interpretation,
        ]
        return "\n".join(lines)

    @staticmethod
    def save_json(path: str | Path, payload: Dict[str, Any]):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
