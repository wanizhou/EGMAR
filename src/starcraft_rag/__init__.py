"""StarCraft II RAG agent framework."""

import sys
from pathlib import Path

MY_KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
if str(MY_KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(MY_KNOWLEDGE_DIR))

from starcraft_rag.pipeline import StarCraftRAGPipeline

__all__ = ["StarCraftRAGPipeline"]
