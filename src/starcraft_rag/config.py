"""Centralized paths and fixed defaults for the streamlined local workflow."""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_ROOT = Path(
    os.environ.get(
        "SC2_MODEL_ROOT",
        PROJECT_ROOT.parents[1] / "my_knowledge" / "starcraft_rag" / "LLM",
    )
)
DEFAULT_RUNTIME_KB = PROJECT_ROOT / "data" / "runtime_kb"
DEFAULT_QA_FILE = PROJECT_ROOT / "data" / "qa" / "qa_dataset_20.jsonl"
REPORTS_DIR = PROJECT_ROOT / "reports"


def model_paths(model_root: str | Path | None = None) -> tuple[Path, Path]:
    """Return the fixed Qwen3-8B and BGE-M3 locations below one model root."""

    root = Path(model_root) if model_root else DEFAULT_MODEL_ROOT
    return root / "Qwen3-8B", root / "bge-m3"
