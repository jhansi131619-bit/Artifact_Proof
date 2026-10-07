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

## Synthetic visual-state methodology

The synthetic benchmark uses a seeded random generator. Heap programs never pop an
empty heap, and DSU indices are always within the configured universe. Instrumented
reference implementations execute the operations and record one initial state plus one
state for every operation.

Every rendered frame is paired with the canonical post-operation state. Model responses
must be JSON and are scored with parse rate, exact state match, field accuracy,
per-structure accuracy, and whole-sequence accuracy. A failed parse receives no correct
fields. Exact match intentionally remains strict: heap array order and DSU parent arrays
are part of the expected answer.

The structural benchmark checks the min-heap property for every heap snapshot and checks
DSU parent bounds and component/root counts for every union-find snapshot. Structural
success validates the corpus generator; it does not measure model quality.
