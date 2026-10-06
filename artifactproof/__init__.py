"""ArtifactProof package."""

from .config import ArtifactSpec, ConsumerSpec, RequirementSpec, TestSpec
from .requirement_parser import parse_requirement_file

__all__ = [
    "ArtifactSpec",
    "ConsumerSpec",
    "RequirementSpec",
    "TestSpec",
    "parse_requirement_file",
]
