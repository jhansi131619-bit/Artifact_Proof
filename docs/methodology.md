# Methodology

ArtifactProof is deliberately conservative. It does not claim to prove correctness or causality in a universal sense. Instead, it provides additional evidence that a required software artifact is implicated in the tested behavior.

The prototype:

- parses structured requirement specifications;
- validates structural existence and references;
- runs the normal tests on the project;
- ablates the requested component in a temporary copy;
- re-runs only the relevant tests;
- computes a prototype Artifact Causal Score;
- reports whether the behavior appears to depend on the requested artifact.

This is a practical measurement for local validation of small software-engineering tasks and a research prototype for eventual extension to richer automated requirement extraction and dependency analysis.
