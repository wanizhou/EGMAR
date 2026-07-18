"""Generate grounded QA rows through an explicitly supplied OpenAI-compatible API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib import request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from starcraft_rag.config import DEFAULT_RUNTIME_KB, REPORTS_DIR


def load_documents() -> list[dict]:
    path = DEFAULT_RUNTIME_KB / "rag_documents.jsonl"
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def call_api(api_base: str, api_key: str, model: str, document: dict) -> dict:
    prompt = (
        "Create one factual StarCraft II QA pair from the supplied source. Return only JSON with "
        "keys question and reference_answer. Do not mention a database, document, or source.\n\n"
        f"Source:\n{document.get('text', '')}"
    )
    payload = {"model": model, "temperature": 0.3, "max_tokens": 300, "messages": [{"role": "user", "content": prompt}]}
    req = request.Request(
        api_base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=90) as response:
        body = json.loads(response.read().decode("utf-8"))
    text = body["choices"][0]["message"].get("content", "").strip()
    if text.startswith("```"):
        text = text.strip("`").removeprefix("json").strip()
    result = json.loads(text)
    if not result.get("question") or not result.get("reference_answer"):
        raise ValueError("API response has no usable question/reference_answer")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate QA data. This is the only project workflow that uses an API.")
    parser.add_argument("--api-key", default=os.environ.get("QA_API_KEY"), help="API key; alternatively set QA_API_KEY.")
    parser.add_argument("--api-base", default=os.environ.get("QA_API_BASE", "https://api.siliconflow.cn/v1"))
    parser.add_argument("--api-model", default=os.environ.get("QA_API_MODEL", "deepseek-ai/DeepSeek-V3.1-Terminus"))
    parser.add_argument("--count", type=int, default=20, help="Number of QA pairs to generate.")
    args = parser.parse_args()
    if not args.api_key:
        parser.error("--api-key is required (or set QA_API_KEY); it is never stored in this repository.")
    if args.count < 1:
        parser.error("--count must be positive")

    docs = load_documents()
    rows, failures = [], []
    for index in range(args.count):
        try:
            qa = call_api(args.api_base, args.api_key, args.api_model, docs[index % len(docs)])
            qa["id"] = f"generated_{index + 1:04d}"
            rows.append(qa)
        except Exception as exc:
            failures.append(f"{index + 1}: {type(exc).__name__}: {exc}")
        print(f"[{index + 1}/{args.count}] accepted={len(rows)} failed={len(failures)}", flush=True)

    run_dir = REPORTS_DIR / "qa_generation" / datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=False)
    output = run_dir / "qa_dataset.jsonl"
    output.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    report = run_dir / "qa_generation_report.md"
    report.write_text(
        "# QA Generation Report\n\n"
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- API model: `{args.api_model}`\n"
        f"- Requested / accepted / failed: {args.count} / {len(rows)} / {len(failures)}\n"
        f"- Dataset: `{output.name}`\n\n"
        + ("## Failures\n\n" + "\n".join(f"- {item}" for item in failures) + "\n" if failures else ""),
        encoding="utf-8",
    )
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
