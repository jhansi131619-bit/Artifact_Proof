from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

from .ablation import AblationEngine
from .causal_analyzer import CausalAnalyzer
from .report import ReportBuilder
from .requirement_parser import parse_requirement_file
from .structural_validator import StructuralValidator
from .test_runner import TestRunner


def run_validation(repo_path: str, requirement_path: str, output_dir: str | None = None):
    requirement = parse_requirement_file(requirement_path)
    validator = StructuralValidator(requirement_path)
    structural = validator.validate(repo_path)

    baseline = TestRunner.run_pytest(repo_path, requirement.tests.relevant)
    if baseline.failed > 0:
        raise RuntimeError(f"Functional validation failed before ablation: {baseline.failed} failing tests")

    ablation = AblationEngine.mutate_repository(
        repo_path,
        requirement.artifact.file,
        requirement.ablation.target_function,
        strategy=requirement.ablation.strategy,
        return_value=requirement.ablation.return_value,
    )
    post = TestRunner.run_pytest(ablation.mutated_repo, requirement.tests.relevant)

    causal = CausalAnalyzer.analyze(
        baseline_passed=baseline.passed,
        baseline_total=baseline.total_tests,
        post_passed=post.passed,
        post_total=post.total_tests,
        relevant_tests=requirement.tests.relevant,
        structural_evidence=structural,
    )

    report = ReportBuilder.render_text(requirement, structural, baseline, post, causal)
    payload = {
        "requirement": asdict(requirement),
        "structural_validation": structural,
        "baseline": baseline.to_dict(),
        "post_ablation": post.to_dict(),
        "causal_analysis": causal.to_dict(),
        "terminal_report": report,
    }

    output_root = Path(output_dir) if output_dir else Path("results")
    output_root.mkdir(parents=True, exist_ok=True)
    ReportBuilder.save_json(output_root / "report.json", payload)
    (output_root / "report.txt").write_text(report, encoding="utf-8")
    return payload


def main():
    parser = argparse.ArgumentParser(description="ArtifactProof CLI")
    parser.add_argument("--repo", required=True, help="Repository to validate")
    parser.add_argument("--requirement", required=True, help="Requirement YAML file")
    parser.add_argument("--output-dir", default="results", help="Directory for JSON/text outputs")
    args = parser.parse_args()
    result = run_validation(args.repo, args.requirement, args.output_dir)
    print(result["terminal_report"])


if __name__ == "__main__":
    main()
