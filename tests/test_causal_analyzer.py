from artifactproof.causal_analyzer import CausalAnalyzer


def test_causal_analyzer_confirms_dependency_when_ablation_breaks_behavior():
    result = CausalAnalyzer.analyze(
        baseline_passed=3,
        baseline_total=3,
        post_passed=0,
        post_total=3,
        relevant_tests=["tests/test_discount.py"],
        structural_evidence={"status": "PASS"},
    )
    assert result.status == "CONFIRMED"
    assert result.artifact_causal_score == 1.0
