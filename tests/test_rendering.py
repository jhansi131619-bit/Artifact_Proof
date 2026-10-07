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
