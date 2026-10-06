# Architecture

ArtifactProof follows a simple validation pipeline:

1. Parse a structured requirement specification.
2. Analyze the repository structure.
3. Run the project's normal tests.
4. Validate the required artifact and consumer structurally.
5. Copy the repository to a temporary directory.
6. Neutralize the target artifact function.
7. Re-run relevant tests.
8. Compute an experimental Artifact Causal Score.
9. Produce a verdict and evidence report.

The modules are intentionally small so they can be extended with additional requirement forms, mutation strategies, and richer dependency analysis.
