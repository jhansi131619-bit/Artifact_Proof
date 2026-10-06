from __future__ import annotations

from pathlib import Path


class RepositoryAnalyzer:
    @staticmethod
    def list_python_files(repo_root: str | Path):
        root = Path(repo_root)
        return sorted(str(path.relative_to(root)) for path in root.rglob("*.py") if path.is_file())
