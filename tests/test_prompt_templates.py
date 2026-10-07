from artifactproof.synthetic import Operation, StructureKind
from artifactproof.synthetic.prompts import PROMPT_VERSION, render_state_prompt


def test_heap_prompt_defines_order_and_result_semantics() -> None:
    prompt = render_state_prompt(StructureKind.HEAP, Operation("push", (-4,)))

    assert f"Prompt-Version: {PROMPT_VERSION}" in prompt
    assert "structure.push(-4)" in prompt
    assert "root first" in prompt
    assert '"values"' in prompt
    assert "negative values" in prompt


def test_dsu_prompt_defines_parent_and_query_semantics() -> None:
    prompt = render_state_prompt(StructureKind.DSU, Operation("find", (3,)))

    assert "structure.find(3)" in prompt
    assert "roots point to themselves" in prompt
    assert '"components"' in prompt
    assert "root index" in prompt
