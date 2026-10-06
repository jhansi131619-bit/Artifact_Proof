from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, List, Optional


@dataclass
class TestRunResult:
    repo_path: str
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    exit_code: int = 0
    runtime_seconds: float = 0.0
    test_names: List[str] = None
    stdout: str = ""
    stderr: str = ""
    command: List[str] = None

    def __post_init__(self):
        if self.test_names is None:
            self.test_names = []
        if self.command is None:
            self.command = []

    def to_dict(self) -> dict:
        return asdict(self)

    def save_json(self, path: str | Path):
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


class TestRunner:
    @staticmethod
    def collect_test_names(repo_root: str | Path, tests: Optional[List[str]] = None) -> List[str]:
        root = Path(repo_root)
        if tests:
            selection = [str(root / item).replace('\\', '/') for item in tests]
        else:
            selection = [str(root)]
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", *selection]
        completed = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
        names: List[str] = []
        for line in completed.stdout.splitlines():
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("=") and not cleaned.startswith("<"):
                names.append(cleaned)
        return names

    @classmethod
    def run_pytest(cls, repo_root: str | Path, tests: Optional[List[str]] = None) -> TestRunResult:
        root = Path(repo_root)
        target_tests = []
        if tests:
            target_tests = [str(item) for item in tests]

        cmd = [sys.executable, "-m", "pytest", "-q", *target_tests]
        started = time.time()
        completed = subprocess.run(cmd, cwd=str(root), capture_output=True, text=True)
        runtime = time.time() - started

        total = 0
        passed = 0
        failed = 0
        skipped = 0
        match = re.search(r"(\d+) passed|\b(\d+) failed|\b(\d+) skipped", completed.stdout + "\n" + completed.stderr, re.IGNORECASE)
        if match:
            # fallback: parse the full output in a simple way
            counts = re.findall(r"(\d+)\s+(passed|failed|skipped)", completed.stdout + "\n" + completed.stderr, re.IGNORECASE)
            for value, label in counts:
                if label.lower() == "passed":
                    passed = int(value)
                elif label.lower() == "failed":
                    failed = int(value)
                elif label.lower() == "skipped":
                    skipped = int(value)
        else:
            if "passed" in completed.stdout.lower() or "failed" in completed.stdout.lower() or "skipped" in completed.stdout.lower():
                pass

        if passed == 0 and failed == 0 and skipped == 0:
            if "passed" in completed.stdout.lower():
                for token in re.findall(r"(\d+) passed", completed.stdout, re.IGNORECASE):
                    passed = int(token)
            if "failed" in completed.stdout.lower():
                for token in re.findall(r"(\d+) failed", completed.stdout, re.IGNORECASE):
                    failed = int(token)
            if "skipped" in completed.stdout.lower():
                for token in re.findall(r"(\d+) skipped", completed.stdout, re.IGNORECASE):
                    skipped = int(token)

        total = passed + failed + skipped
        return TestRunResult(
            repo_path=str(root),
            total_tests=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            exit_code=completed.returncode,
            runtime_seconds=runtime,
            test_names=cls.collect_test_names(root, target_tests),
            stdout=completed.stdout,
            stderr=completed.stderr,
            command=cmd,
        )
