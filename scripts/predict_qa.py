"""Run the fixed local RAG workflow and save only the final predictions."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from starcraft_rag.config import DEFAULT_QA_FILE, REPORTS_DIR
from query import build_pipeline


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def cell(value: object) -> str:
    return " ".join(str(value or "").split()).replace("|", "/")


def render_results(rows: list[dict[str, Any]], qa_file: Path, model_root: str | None) -> str:
    """Render predictions only; no reference answers, scores, or pass/fail labels."""

    lines = [
        "# Local RAG Prediction Results",
        "",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        "- Workflow: local Qwen3-8B router + BGE-M3 retrieval + local agents + local answer synthesis",
        f"- Question file: `{qa_file}`",
        f"- Model root: `{model_root or 'default (my_knowledge/starcraft_rag/LLM)'}`",
        f"- Predictions: {len(rows)}",
        "",
        "| ID | Question | Prediction |",
        "| --- | --- | --- |",
    ]
    for row in rows:
        prediction = row["prediction"] or (f"Prediction error: {row['error']}" if row["error"] else "")
        lines.append(f"| {cell(row['id'])} | {cell(row['question'])} | {cell(prediction)} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local RAG predictions without an evaluation step.")
    parser.add_argument("--model-root", help="Folder containing Qwen3-8B and bge-m3.")
    parser.add_argument("--questions", type=Path, default=DEFAULT_QA_FILE, help="Question JSONL file (default: bundled 20 QA).")
    parser.add_argument("--limit", type=int, help="Predict only the first N questions.")
    args = parser.parse_args()

    questions = read_jsonl(args.questions)
    if args.limit is not None:
        questions = questions[: args.limit]
    if not questions:
        raise ValueError("No question rows selected")

    run_dir = REPORTS_DIR / "predictions" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    json_path = run_dir / "predictions.json"
    markdown_path = run_dir / "prediction_results.md"
    rows: list[dict[str, Any]] = []

    def checkpoint() -> None:
        json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        markdown_path.write_text(render_results(rows, args.questions, args.model_root), encoding="utf-8")

    pipeline = build_pipeline(args.model_root)
    for index, item in enumerate(questions, start=1):
        question = str(item.get("question") or "").strip()
        if not question:
            raise ValueError(f"Question row {index} has no question field")
        try:
            prediction = str(pipeline.answer(question).answer or "").strip()
            error = ""
        except Exception as exc:  # Keep a result row for every supplied question.
            prediction = ""
            error = f"{type(exc).__name__}: {exc}"
        rows.append({"id": item.get("id") or f"question_{index:06d}", "question": question, "prediction": prediction, "error": error})
        checkpoint()
        print(f"[{index}/{len(questions)}] {rows[-1]['id']}", flush=True)

    print(f"Prediction results: {markdown_path}")


if __name__ == "__main__":
    main()
