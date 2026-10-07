"""PNG rendering for synthetic data-structure states and traces."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .types import Operation, StructureKind, Trace


@dataclass(frozen=True, slots=True)
class RenderTheme:
    width: int = 800
    height: int = 520
    background: str = "#f8fafc"
    foreground: str = "#172033"
    edge: str = "#64748b"
    node_fill: str = "#dbeafe"
    touched_fill: str = "#fbbf24"
    root_fill: str = "#a7f3d0"
    caption_fill: str = "#ffffff"


class StateRenderer:
    def __init__(self, theme: RenderTheme | None = None) -> None:
        self.theme = theme or RenderTheme()
        if self.theme.width < 320 or self.theme.height < 240:
            raise ValueError("render dimensions must be at least 320x240")
        self.font = ImageFont.load_default()

    def render_state(
        self,
        structure: StructureKind,
        state: dict[str, Any],
        destination: str | Path,
        *,
        step: int = 0,
        operation: Operation | None = None,
    ) -> Path:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        image = Image.new("RGB", (self.theme.width, self.theme.height), self.theme.background)
        draw = ImageDraw.Draw(image)
        if structure is StructureKind.HEAP:
            self._draw_heap(draw, state)
        elif structure is StructureKind.DSU:
            self._draw_dsu(draw, state)
        else:  # pragma: no cover - protected by the enum
            raise ValueError(f"unsupported structure: {structure}")
        self._draw_caption(draw, structure, state, step, operation)
        image.save(path, format="PNG", optimize=True)
        return path

    def render_trace(self, trace: Trace, output_dir: str | Path) -> list[Path]:
        trace.validate()
        directory = Path(output_dir) / trace.example_id
        directory.mkdir(parents=True, exist_ok=True)
        frames: list[Path] = []
        for step, state in enumerate(trace.states):
            operation = trace.operations[step - 1] if step else None
            frames.append(
                self.render_state(
                    trace.structure,
                    state,
                    directory / f"frame-{step:03d}.png",
                    step=step,
                    operation=operation,
                )
            )
        manifest = {
            "example_id": trace.example_id,
            "structure": trace.structure.value,
            "frames": [frame.name for frame in frames],
            "operations": [operation.to_dict() for operation in trace.operations],
            "render_theme": asdict(self.theme),
        }
        (directory / "manifest.json").write_text(
            json.dumps(manifest, indent=2),
            encoding="utf-8",
        )
        return frames

    def _draw_heap(self, draw: ImageDraw.ImageDraw, state: dict[str, Any]) -> None:
        values = state.get("values", [])
        touched = set(state.get("touched", []))
        if not values:
            self._centered_text(draw, "Empty heap", self.theme.height // 2)
            return
        positions: list[tuple[float, float]] = []
        top = 88
        usable_height = self.theme.height - top - 92
        levels = max(1, math.ceil(math.log2(len(values) + 1)))
        level_gap = usable_height / max(1, levels - 1)
        for index in range(len(values)):
            level = int(math.log2(index + 1))
            first = (1 << level) - 1
            offset = index - first
            slots = 1 << level
            x = self.theme.width * (offset + 1) / (slots + 1)
            y = top + level * level_gap
            positions.append((x, y))
        for index in range(1, len(values)):
            draw.line([positions[(index - 1) // 2], positions[index]], fill=self.theme.edge, width=3)
        for index, (x, y) in enumerate(positions):
            fill = self.theme.touched_fill if index in touched else self.theme.node_fill
            self._node(draw, x, y, str(values[index]), fill)

    def _draw_dsu(self, draw: ImageDraw.ImageDraw, state: dict[str, Any]) -> None:
        parents = state.get("parents", [])
        touched = set(state.get("touched", []))
        if not parents:
            self._centered_text(draw, "Empty DSU", self.theme.height // 2)
            return
        columns = max(1, math.ceil(math.sqrt(len(parents))))
        rows = math.ceil(len(parents) / columns)
        x_gap = self.theme.width / (columns + 1)
        y_gap = (self.theme.height - 150) / (rows + 1)
        positions = [
            (x_gap * (index % columns + 1), 95 + y_gap * (index // columns + 1))
            for index in range(len(parents))
        ]
        for child, parent in enumerate(parents):
            if child != parent:
                draw.line([positions[child], positions[parent]], fill=self.theme.edge, width=3)
        for index, (x, y) in enumerate(positions):
            if index in touched:
                fill = self.theme.touched_fill
            elif parents[index] == index:
                fill = self.theme.root_fill
            else:
                fill = self.theme.node_fill
            self._node(draw, x, y, str(index), fill)

    def _draw_caption(
        self,
        draw: ImageDraw.ImageDraw,
        structure: StructureKind,
        state: dict[str, Any],
        step: int,
        operation: Operation | None,
    ) -> None:
        draw.rounded_rectangle(
            (20, 16, self.theme.width - 20, 66),
            radius=10,
            fill=self.theme.caption_fill,
            outline=self.theme.edge,
        )
        title = f"{structure.value.upper()} · step {step}"
        if operation:
            title += f" · {operation.to_code()}"
        if state.get("result") is not None:
            title += f" · result={state['result']}"
        draw.text((36, 35), title, fill=self.theme.foreground, font=self.font, anchor="lm")

    def _node(
        self,
        draw: ImageDraw.ImageDraw,
        x: float,
        y: float,
        label: str,
        fill: str,
    ) -> None:
        radius = 24
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=fill,
            outline=self.theme.foreground,
            width=3,
        )
        draw.text((x, y), label, fill=self.theme.foreground, font=self.font, anchor="mm")

    def _centered_text(self, draw: ImageDraw.ImageDraw, label: str, y: int) -> None:
        draw.text(
            (self.theme.width // 2, y),
            label,
            fill=self.theme.foreground,
            font=self.font,
            anchor="mm",
        )
