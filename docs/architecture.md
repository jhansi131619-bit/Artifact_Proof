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

## Synthetic benchmark architecture

The `artifactproof.synthetic` package is a separate, composable pipeline:

```text
GeneratorConfig
      |
      v
Program JSONL -----> HeapMachine / DSUMachine
                           |
                           v
                      Trace JSONL
                           |
                           v
                    StateRenderer -----> PNG frames + manifests
                           |
                           v
                    VisionModel adapter
                           |
                           v
                 Evaluation JSONL -----> metrics.json
```

Programs contain operations but no answers. State machines execute those programs and
produce the canonical trace. This separation keeps random generation independently
testable and prevents rendered labels from becoming the source of truth.

`StateRenderer` only consumes traces. `MultimodalEvaluator` only consumes traces and
rendered frames through the small `VisionModel` protocol. The included
`HTTPVisionModel` is therefore replaceable without changing generation, rendering, or
scoring.
