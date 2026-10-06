from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass
class CausalResult:
    relevant_tests_before: int = 0
    relevant_tests_after: int = 0
    tests_affected: int = 0
    tests_unaffected: int = 0
    artifact_causal_score: float = 0.0
    status: str = "INCONCLUSIVE"
    warning_flags: List[str] = None
    interpretation: str = ""

    def __post_init__(self):
        if self.warning_flags is None:
            self.warning_flags = []

    def to_dict(self):
        return asdict(self)


class CausalAnalyzer:
    @staticmethod
    def analyze(
        baseline_passed: int,
        baseline_total: int,
        post_passed: int,
        post_total: int,
        relevant_tests: List[str] | None = None,
        structural_evidence: Dict[str, Any] | None = None,
    ) -> CausalResult:
        relevant = relevant_tests or []
        before = max(0, baseline_passed)
        after = max(0, post_passed)
        affected = max(0, before - after)
        unaffected = max(0, before - affected)
        denominator = before if before else 1
        acs = 0.0 if before == 0 else (affected / denominator)

        warnings = []
        if before == 0:
            warnings.append("No relevant tests passed before ablation.")
        if structural_evidence and structural_evidence.get("status") not in (None, "PASS"):
            warnings.append("Structural validation did not pass.")
        if before > 0 and acs == 0:
            warnings.append("Neutralizing the artifact did not affect any passing relevant test.")

        if before > 0 and acs > 0:
            status = "CONFIRMED"
            interpretation = "Evidence suggests the requested artifact measurably controlled the validated behaviour."
        elif before == 0:
            status = "INCONCLUSIVE"
            interpretation = "No relevant passing baseline was available, so the causal evidence is inconclusive."
        elif acs == 0:
            status = "SUSPICIOUS"
            interpretation = "The requested artifact appears structurally present but did not measurably affect the relevant validated behaviour."
        else:
            status = "INCONCLUSIVE"
            interpretation = "The result is mixed and should be interpreted with caution."

        if structural_evidence and structural_evidence.get("artifact_file_exists") is False:
            status = "STRUCTURAL_FAILURE"
            interpretation = "The required artifact was not present, so the causal validation could not proceed meaningfully."

        return CausalResult(
            relevant_tests_before=before,
            relevant_tests_after=after,
            tests_affected=affected,
            tests_unaffected=unaffected,
            artifact_causal_score=round(acs, 4),
            status=status,
            warning_flags=warnings,
            interpretation=interpretation,
        )
