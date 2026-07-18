from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from starcraft_rag.config import DEFAULT_QA_FILE, DEFAULT_RUNTIME_KB, model_paths
from starcraft_rag.kb import KBStore


class OfflineProjectTests(unittest.TestCase):
    def test_bundled_knowledge_base_loads(self) -> None:
        store = KBStore(DEFAULT_RUNTIME_KB)
        self.assertGreater(len(store.rag_documents), 100)
        self.assertTrue((DEFAULT_RUNTIME_KB / "vector_index" / "bge_m3" / "manifest.json").is_file())

    def test_qa_smoke_dataset_has_twenty_valid_rows(self) -> None:
        rows = [json.loads(line) for line in DEFAULT_QA_FILE.read_text(encoding="utf-8-sig").splitlines() if line]
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(row.get("question") and row.get("reference_answer") for row in rows))

    def test_model_root_has_fixed_child_names(self) -> None:
        qwen, bge = model_paths()
        self.assertEqual(qwen.name, "Qwen3-8B")
        self.assertEqual(bge.name, "bge-m3")

    def test_project_exposes_prediction_not_evaluation_script(self) -> None:
        self.assertTrue((ROOT / "scripts" / "predict_qa.py").is_file())
        self.assertFalse((ROOT / "scripts" / "evaluate.py").exists())


if __name__ == "__main__":
    unittest.main()
