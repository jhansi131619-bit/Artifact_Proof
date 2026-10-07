import json

from PIL import Image, ImageChops

from artifactproof.synthetic import (
    Operation,
    Program,
    StateRenderer,
    StructureKind,
    execute_dsu,
    execute_heap,
)
from artifactproof.synthetic.cli import main
from artifactproof.synthetic.dataset import write_jsonl


def test_heap_trace_renders_png_frames_and_manifest(tmp_path) -> None:
    trace = execute_heap(
        Program(
            example_id="heap-render",
            structure=StructureKind.HEAP,
            operations=[Operation("push", (7,)), Operation("push", (2,))],
            metadata={"heap_order": "min"},
        )
    )

    frames = StateRenderer().render_trace(trace, tmp_path)

    assert len(frames) == 3
    assert all(frame.exists() for frame in frames)
    image = Image.open(frames[-1])
    assert image.size == (800, 520)
    background = Image.new("RGB", image.size, "#f8fafc")
    assert ImageChops.difference(image.convert("RGB"), background).getbbox() is not None
    manifest = json.loads((tmp_path / "heap-render" / "manifest.json").read_text())
    assert manifest["frames"] == ["frame-000.png", "frame-001.png", "frame-002.png"]


def test_dsu_trace_renders_all_states(tmp_path) -> None:
    trace = execute_dsu(
        Program(
            example_id="dsu-render",
            structure=StructureKind.DSU,
            operations=[Operation("union", (0, 1)), Operation("connected", (0, 2))],
            metadata={"size": 3},
        )
    )

    assert len(StateRenderer().render_trace(trace, tmp_path)) == 3


def test_execute_and_render_cli_pipeline(tmp_path) -> None:
    programs_path = tmp_path / "programs.jsonl"
    traces_path = tmp_path / "traces.jsonl"
    images_path = tmp_path / "images"
    write_jsonl(
        [
            Program(
                example_id="heap-cli",
                structure=StructureKind.HEAP,
                operations=[Operation("push", (4,))],
                metadata={"heap_order": "min"},
            )
        ],
        programs_path,
    )

    assert main(["execute", "--input", str(programs_path), "--output", str(traces_path)]) == 0
    assert main(["render", "--input", str(traces_path), "--output-dir", str(images_path)]) == 0
    assert (images_path / "heap-cli" / "frame-001.png").exists()


def test_heap_layout_handles_partial_and_dense_levels() -> None:
    renderer = StateRenderer()

    partial_positions, partial_radius = renderer._heap_layout(5)
    dense_positions, dense_radius = renderer._heap_layout(63)

    assert partial_positions[0][0] == 400
    assert partial_positions[1][0] == 200
    assert partial_positions[2][0] == 600
    assert partial_positions[3][0] == 100
    assert partial_radius == 24
    assert dense_radius >= 6
    assert all(
        dense_radius <= x <= renderer.theme.width - dense_radius
        for x, _ in dense_positions
    )
    deepest = dense_positions[31:]
    assert all(
        right[0] - left[0] >= dense_radius * 2
        for left, right in zip(deepest, deepest[1:])
    )


def test_heap_renderer_handles_empty_single_and_unusual_values(tmp_path) -> None:
    renderer = StateRenderer()
    states = [
        {"values": [], "result": None, "touched": [0]},
        {"values": [-9999], "result": None, "touched": [0]},
        {"values": [-2, -2, 100000], "result": None, "touched": [1, 2]},
        {"values": list(range(63)), "result": None, "touched": [62]},
    ]

    for index, state in enumerate(states):
        path = renderer.render_state(
            StructureKind.HEAP,
            state,
            tmp_path / f"edge-{index}.png",
            step=index,
            operation=Operation("push", (10**30,)),
        )
        with Image.open(path) as image:
            assert image.size == (800, 520)
