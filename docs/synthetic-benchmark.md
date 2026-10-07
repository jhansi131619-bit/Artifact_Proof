# Synthetic heap and DSU benchmark

## What it measures

This benchmark tests exact visual state recovery after data-structure operations. It
supports min-heaps and disjoint-set union (DSU/union-find) with path compression and
union by rank.

Each example passes through five stages:

1. Generate a deterministic operation program.
2. Execute the program and record canonical snapshots.
3. Render the snapshots as PNG diagrams.
4. Send each post-operation frame and a versioned prompt to a vision model.
5. Parse JSON responses and aggregate evaluation metrics.

## Configuration

The reference configuration is `experiments/synthetic_benchmark.yaml`. Important fields
are:

- `generation.seed` for reproducibility;
- `examples_per_structure` and operation bounds for corpus size;
- DSU size and heap value bounds;
- render dimensions and colours;
- the optional model endpoint, name, timeout, and API-key environment variable.

When `model.enabled` is false, `run` stops after rendering. When it is true, evaluation
and metric files are also produced.

## Model endpoint contract

`HTTPVisionModel` sends an HTTP `POST` request with this shape:

```json
{
  "model": "local-vision-model",
  "prompt": "Prompt-Version: state-extraction-v2 ...",
  "images": [
    {"mime_type": "image/png", "data": "<base64>"}
  ]
}
```

If the configured API-key environment variable exists, the request includes
`Authorization: Bearer <token>`. The endpoint must return:

```json
{"output": "{\"values\": [2, 5], \"result\": null}"}
```

The `output` value is the model's raw text. JSON code fences are accepted, but prose or
non-object JSON is recorded as a parse error.

## Output layout

```text
results/synthetic/
  programs.jsonl
  traces.jsonl
  run.json
  images/
    heap-00000/
      frame-000.png
      frame-001.png
      manifest.json
  evaluations.jsonl  # only when model evaluation is enabled
  metrics.json        # only when model evaluation is enabled
```

The initial frame is numbered `000`. Evaluation begins at frame `001`, because each
scored sample corresponds to the state after an operation.

## Reproducibility

Run the structural benchmark with:

```bash
python experiments/run_synthetic_benchmark.py
```

The result is written to `results/synthetic_benchmark_summary.json`. Re-running with the
checked-in configuration should reproduce the same corpus statistics and invariant
counts.
