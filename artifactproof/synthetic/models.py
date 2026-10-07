"""Adapters for multimodal model inference."""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


class VisionModel(Protocol):
    """Minimal interface required by the evaluation pipeline."""

    @property
    def name(self) -> str: ...

    def predict(self, prompt: str, images: Sequence[Path]) -> str: ...


@dataclass(slots=True)
class HTTPVisionModel:
    """Call a JSON-over-HTTP endpoint that accepts prompts and base64 images."""

    endpoint: str
    model: str
    api_key_env: str = "ARTIFACTPROOF_MODEL_API_KEY"
    timeout_seconds: float = 60.0

    @property
    def name(self) -> str:
        return self.model

    def predict(self, prompt: str, images: Sequence[Path]) -> str:
        encoded_images = []
        for image in images:
            mime_type = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
            encoded_images.append(
                {
                    "mime_type": mime_type,
                    "data": base64.b64encode(image.read_bytes()).decode("ascii"),
                }
            )
        payload = json.dumps(
            {"model": self.model, "prompt": prompt, "images": encoded_images}
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        api_key = os.environ.get(self.api_key_env)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        request = urllib.request.Request(
            self.endpoint,
            data=payload,
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            result = json.loads(response.read().decode("utf-8"))
        if not isinstance(result.get("output"), str):
            raise ValueError("model endpoint response must contain a string 'output'")
        return result["output"]
