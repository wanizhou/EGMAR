# EGMAR

[English](README.md) | [简体中文](README.zh-CN.md)

Evidence-Grounded Multi-Agent Reasoning for Strategic Decision-Making in StarCraft II

EGMAR supports knowledge-based question answering and strategic decision-making in StarCraft II. It organizes game knowledge into structured profiles, assigns evidence-selection tasks to specialized agents, and synthesizes answers with source references.

This repository provides the initial open-source implementation accompanying the paper, including local question answering, batch prediction, a runtime knowledge base, QA datasets, and an API-based QA generation tool. The default workflow uses local Qwen3-8B and BGE-M3 models.

## Method overview

```text
Question -> Query routing -> BGE-M3 hybrid retrieval
         -> Profile resolution -> Agent evidence selection -> Answer synthesis
```

Retrieval combines dense semantic vectors, sparse lexical weights, and document metadata. Retrieved documents link to structured profiles, allowing agents to select evidence from specific fields and retain source information.

| Agent | Responsibilities |
| --- | --- |
| `UnitProfileAgent` | Unit and building attributes, combat capabilities, and tactical information |
| `AbilityAgent` | Ability effects, properties, and usage constraints |
| `CounterAgent` | Counter relations and applicable conditions |
| `TechTreeAgent` | Production costs, prerequisites, and upgrades |
| `ScenarioRouterAgent` | Scenario descriptions, triggers, and related knowledge |

Routing, agent reasoning, and answer synthesis share one local Qwen3-8B provider. Agent tasks run sequentially, and the synthesis output includes supporting evidence, uncertainties, and conflicts.

## Repository structure

```text
EGMAR/
├── data/
│   ├── runtime_kb/          # Structured profiles, RAG documents, and BGE-M3 index
│   ├── qa/                  # 20-item and 1,000-item QA datasets
│   └── 逐题审核明细.md        # Review records for 100 QA pairs
├── scripts/
│   ├── query.py             # Single-question inference
│   ├── predict_qa.py        # Batch prediction
│   └── generate_qa.py       # API-based QA generation
├── src/starcraft_rag/       # Routing, retrieval, agents, and answer synthesis
├── reports/                # Prediction and QA generation outputs
├── tests/test_offline.py   # Offline structure and data checks
└── requirements.txt
```

## Installation and models

Use Python 3.10 or later and a PyTorch installation compatible with your CUDA or CPU environment.

```powershell
git clone https://github.com/wanizhou/EGMAR.git
cd EGMAR
python -m pip install -r requirements.txt
```

Place the Qwen3-8B and BGE-M3 model weights, configuration, and tokenizer files under a common model root. The Qwen3-8B tokenizer must support a chat template.

```text
<model-root>/
├── Qwen3-8B/
└── bge-m3/
```

Set the model root in PowerShell.

```powershell
$env:SC2_MODEL_ROOT = "E:\models\starcraft_llm"
```

You can also pass `--model-root "E:\models\starcraft_llm"` to the inference commands. This argument takes precedence over `SC2_MODEL_ROOT`.

A CUDA GPU is recommended. The local language model defaults to FP16 with `device_map="auto"`. The retriever automatically rebuilds its index when the documents, model path, or encoding settings change.

## Usage

Run the following commands from the repository root.

### Single-question inference

```powershell
python scripts/query.py "How do I counter Dark Templar?"
python scripts/query.py "What are the prerequisites for producing a Colossus?" --json
```

The default output is the answer text. Add `--json` to inspect the query plan, retrieved documents, agent evidence, and synthesis output.

### Batch prediction

Start with a few questions, or select one of the bundled datasets.

```powershell
python scripts/predict_qa.py --limit 3
python scripts/predict_qa.py --questions data/qa/qa_dataset_20.jsonl
python scripts/predict_qa.py --questions data/qa/qa_dataset_1000.jsonl
```

| Argument | Purpose |
| --- | --- |
| `--model-root` | Model root containing `Qwen3-8B` and `bge-m3` |
| `--questions` | Input JSONL file, defaulting to the 20-item dataset |
| `--limit` | Process only the first N questions |

Custom inputs use one JSON object per line, with a required `question` field and an optional `id`.

```json
{"id": "question_001", "question": "How do I counter Dark Templar?"}
```

Each run saves `prediction_results.md` and `predictions.json` under `reports/predictions/<timestamp>/`, updating the files after each question.

## Knowledge base and QA datasets

### Structured knowledge base

The runtime knowledge base is stored in `data/runtime_kb/`.

| File | Content |
| --- | --- |
| `entity_profiles.jsonl` | Unit and building attributes, costs, abilities, and technology information |
| `ability_profiles.jsonl` | Ability effects, metrics, and constraints |
| `relation_profiles.jsonl` | Structured relations and applicable conditions |
| `scenario_profiles.jsonl` | Scenario tags, descriptions, and related knowledge |
| `rag_documents.jsonl` | Retrieval text, metadata, and profile references |

Knowledge entries distinguish processed explicit facts (`processed`) from knowledge derived through rules (`enriched`). Agent evidence retains references to the source profiles and fields.

### QA datasets

The datasets cover `single_hop`, `two_hop`, `multi_hop`, and `ambiguous` questions.

| Dataset | Items | Purpose |
| --- | --- | --- |
| `data/qa/qa_dataset_20.jsonl` | 20 | Quick validation of the local workflow |
| `data/qa/qa_dataset_1000.jsonl` | 1,000 | Batch QA experiments and result analysis |

The 1,000-item dataset contains 250 items per category. Records include questions, reference answers, category labels, and generation and validation model metadata. The file `data/逐题审核明细.md` contains review records and proposed answer revisions for 100 QA pairs.

## QA data generation

Generate questions and reference answers from runtime RAG documents through an OpenAI-compatible `/chat/completions` endpoint.

```powershell
$env:QA_API_KEY = "your-api-key"
python scripts/generate_qa.py --count 20
```

| Argument | Environment variable | Default or requirement |
| --- | --- | --- |
| `--api-key` | `QA_API_KEY` | Required |
| `--api-base` | `QA_API_BASE` | `https://api.siliconflow.cn/v1` |
| `--api-model` | `QA_API_MODEL` | `deepseek-ai/DeepSeek-V3.1-Terminus` |
| `--count` | - | Number of generation attempts, defaulting to 20 |

Outputs are saved as `qa_dataset.jsonl` and `qa_generation_report.md` under `reports/qa_generation/<timestamp>/`.

## Offline validation

```powershell
python -m unittest discover -s tests -p test_offline.py -v
```

These checks cover knowledge-base loading, the index manifest, QA data format, model directory names, and the prediction entry point.

## Planned releases

We plan to release the code for adapting and integrating EGMAR with TextStarCraft II in a future update.
