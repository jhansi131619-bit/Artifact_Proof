from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ArtifactSpec:
    file: str
    class_name: str
    functions: List[str] = field(default_factory=list)


@dataclass
class ConsumerSpec:
    file: str
    class_name: str


@dataclass
class TestSpec:
    relevant: List[str] = field(default_factory=list)


@dataclass
class AblationSpec:
    target_function: str
    strategy: str = "constant_return"
    return_value: Optional[object] = None


@dataclass
class RequirementSpec:
    id: str
    description: str
    artifact: ArtifactSpec
    consumer: ConsumerSpec
    tests: TestSpec
    ablation: AblationSpec
