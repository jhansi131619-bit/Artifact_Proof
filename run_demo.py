from artifactproof.cli import run_validation


if __name__ == "__main__":
    print("Running DiscountEngine correct implementation...")
    correct = run_validation(
        "benchmark/discount_engine/correct",
        "benchmark/discount_engine/requirement.yaml",
        "results/demo_correct",
    )
    print(correct["terminal_report"])
    print("\nRunning DiscountEngine misdelivered implementation...")
    misdelivered = run_validation(
        "benchmark/discount_engine/misdelivered",
        "benchmark/discount_engine/requirement.yaml",
        "results/demo_misdelivered",
    )
    print(misdelivered["terminal_report"])
