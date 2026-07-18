"""Ask one question with the default local BGE + Qwen agent workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from starcraft_rag.config import DEFAULT_RUNTIME_KB, model_paths
from starcraft_rag.llm import TransformersLocalProvider
from starcraft_rag.pipeline import StarCraftRAGPipeline


def build_pipeline(model_root: str | None = None) -> StarCraftRAGPipeline:
    """Build one shared local provider so router, agents, and synthesis share VRAM."""

    qwen_path, bge_path = model_paths(model_root)
    provider = TransformersLocalProvider(qwen_path)
    return StarCraftRAGPipeline(
        runtime_kb_dir=DEFAULT_RUNTIME_KB,
        model_path=qwen_path,
        bge_model_path=bge_path,
        llm_provider=provider,
        agent_llm_provider=provider,
        synthesizer_llm_provider=provider,
        router_mode="local",
        retriever_mode="bge-m3",
        agent_mode="local",
        synthesizer_mode="local",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask one StarCraft II knowledge-base question locally.")
    parser.add_argument("question", help="Question to answer.")
    parser.add_argument("--model-root", help="Folder containing Qwen3-8B and bge-m3.")
    parser.add_argument("--json", action="store_true", help="Print the full pipeline result.")
    args = parser.parse_args()

    result = build_pipeline(args.model_root).answer(args.question)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) if args.json else result.answer)


if __name__ == "__main__":
    main()
