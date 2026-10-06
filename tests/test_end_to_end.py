from artifactproof.cli import run_validation


def test_discount_engine_correct_and_misdelivered_are_distinguished():
    correct = run_validation("benchmark/discount_engine/correct", "benchmark/discount_engine/requirement.yaml", "results/discount_correct")
    misdelivered = run_validation("benchmark/discount_engine/misdelivered", "benchmark/discount_engine/requirement.yaml", "results/discount_misdelivered")

    assert correct["causal_analysis"]["status"] == "CONFIRMED"
    assert misdelivered["causal_analysis"]["status"] == "SUSPICIOUS"
    assert correct["causal_analysis"]["artifact_causal_score"] > misdelivered["causal_analysis"]["artifact_causal_score"]
