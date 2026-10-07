"""Versioned prompt templates for state extraction from benchmark images."""

from __future__ import annotations

from .types import Operation, StructureKind

PROMPT_VERSION = "state-extraction-v2"

_HEAP_TEMPLATE = """Task: recover the exact min-heap state shown in the image.
The image is the state immediately after `{operation}`.

Read every node in array/index order: root first, then each tree level from left to right.
Return exactly one JSON object with this schema:
{{"values": [integer, ...], "result": integer_or_null}}

`result` is the value returned by pop/peek and is null for push. Preserve duplicate and
negative values. Do not include markdown, prose, inferred operations, or extra fields."""

_DSU_TEMPLATE = """Task: recover the exact disjoint-set union state shown in the image.
The image is the state immediately after `{operation}`.

Each numbered node points to its current parent; roots point to themselves. List parents
in node-index order from 0 through n-1. Return exactly one JSON object with this schema:
{{"parents": [integer, ...], "components": integer, "result": integer_boolean_or_null}}

For union/connected, `result` is a boolean. For find, `result` is the root index. Do not
apply any additional path compression. Do not include markdown, prose, or extra fields."""


def render_state_prompt(structure: StructureKind, operation: Operation) -> str:
    template = _HEAP_TEMPLATE if structure is StructureKind.HEAP else _DSU_TEMPLATE
    return f"Prompt-Version: {PROMPT_VERSION}\n\n" + template.format(
        operation=operation.to_code()
    )
