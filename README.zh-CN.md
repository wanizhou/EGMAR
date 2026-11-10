# EGMAR

[English](README.md) | [简体中文](README.zh-CN.md)

Evidence-Grounded Multi-Agent Reasoning for Strategic Decision-Making in StarCraft II

EGMAR 面向星际争霸 II 知识问答与战略决策支持，将游戏知识组织为结构化条目，由专门分工的智能体选择证据，再综合生成带有来源信息的回答。

本仓库提供论文对应的初版开源实现，包含本地问答、批量预测、运行时知识库、QA 数据集和基于 API 的 QA 生成工具。默认流程使用本地 Qwen3-8B 与 BGE-M3 模型。

## 方法概览

```text
用户问题 -> 问题路由 -> BGE-M3 混合检索
         -> 结构化知识回连 -> 智能体证据选择 -> 答案综合
```

检索结合稠密语义向量、稀疏词项权重与文档元数据。召回文档关联到结构化 profile，智能体从具体字段中选择证据并保留来源信息。

| 智能体 | 处理内容 |
| --- | --- |
| `UnitProfileAgent` | 单位和建筑的属性、作战能力与战术信息 |
| `AbilityAgent` | 技能效果、属性与使用约束 |
| `CounterAgent` | 克制关系与适用条件 |
| `TechTreeAgent` | 生产成本、前置条件与升级 |
| `ScenarioRouterAgent` | 场景描述、触发条件与相关知识 |

路由、智能体推理和答案综合共享一个本地 Qwen3-8B provider。智能体任务按序执行，综合结果包含支持证据、不确定性和冲突信息。

## 项目结构

```text
EGMAR/
├── data/
│   ├── runtime_kb/          # 结构化知识、RAG 文档与 BGE-M3 索引
│   ├── qa/                  # 20 条与 1,000 条 QA 数据
│   └── 逐题审核明细.md        # 100 条 QA 的审核记录
├── scripts/
│   ├── query.py             # 单问题问答
│   ├── predict_qa.py        # 批量预测
│   └── generate_qa.py       # 基于 API 的 QA 生成
├── src/starcraft_rag/       # 路由、检索、智能体与答案综合
├── reports/                # 预测和 QA 生成结果
├── tests/test_offline.py   # 离线结构与数据校验
└── requirements.txt
```

## 安装与模型配置

使用 Python 3.10 或更高版本，并根据本机 CUDA 或 CPU 环境安装兼容的 PyTorch。

```powershell
git clone https://github.com/wanizhou/EGMAR.git
cd EGMAR
python -m pip install -r requirements.txt
```

将 Qwen3-8B 与 BGE-M3 的模型权重、配置和 tokenizer 文件放在同一模型根目录下。Qwen3-8B 的 tokenizer 需支持对话模板。

```text
<model-root>/
├── Qwen3-8B/
└── bge-m3/
```

在 PowerShell 中设置模型根目录。

```powershell
$env:SC2_MODEL_ROOT = "E:\models\starcraft_llm"
```

也可在问答命令中传入 `--model-root "E:\models\starcraft_llm"`，该参数优先于 `SC2_MODEL_ROOT`。

推荐使用 CUDA GPU。本地语言模型默认采用 FP16 和 `device_map="auto"`。文档、模型路径或编码配置变化时，检索器会自动重建索引。

## 使用方法

以下命令均在仓库根目录执行。

### 单问题问答

```powershell
python scripts/query.py "How do I counter Dark Templar?"
python scripts/query.py "What are the prerequisites for producing a Colossus?" --json
```

默认输出回答正文。添加 `--json` 可查看查询计划、召回文档、智能体证据与答案综合结果。

### 批量预测

先用少量问题检查流程，或指定随仓库提供的数据集。

```powershell
python scripts/predict_qa.py --limit 3
python scripts/predict_qa.py --questions data/qa/qa_dataset_20.jsonl
python scripts/predict_qa.py --questions data/qa/qa_dataset_1000.jsonl
```

| 参数 | 用途 |
| --- | --- |
| `--model-root` | 包含 `Qwen3-8B` 与 `bge-m3` 的模型根目录 |
| `--questions` | 输入 JSONL 文件，默认使用 20 条 QA 数据 |
| `--limit` | 仅处理前 N 条问题 |

自定义输入采用 JSONL 格式，每行一个 JSON 对象，必需字段为 `question`，可选字段为 `id`。

```json
{"id": "question_001", "question": "How do I counter Dark Templar?"}
```

每次运行在 `reports/predictions/<timestamp>/` 下保存 `prediction_results.md` 和 `predictions.json`，并在处理完每条问题后更新结果。

## 知识库与 QA 数据

### 结构化知识库

运行时知识库位于 `data/runtime_kb/`。

| 文件 | 内容 |
| --- | --- |
| `entity_profiles.jsonl` | 单位和建筑的属性、成本、技能与科技信息 |
| `ability_profiles.jsonl` | 技能效果、指标与约束 |
| `relation_profiles.jsonl` | 结构化关系与适用条件 |
| `scenario_profiles.jsonl` | 场景标签、描述与相关知识 |
| `rag_documents.jsonl` | 检索文本、元数据与 profile 引用 |

知识条目区分整理后的显式事实（`processed`）与规则推导知识（`enriched`）。智能体证据保留对应的 profile 和字段引用。

### QA 数据集

数据覆盖 `single_hop`、`two_hop`、`multi_hop` 和 `ambiguous` 四类问题。

| 数据文件 | 条数 | 用途 |
| --- | --- | --- |
| `data/qa/qa_dataset_20.jsonl` | 20 | 快速验证本地流程 |
| `data/qa/qa_dataset_1000.jsonl` | 1,000 | 批量问答实验与结果分析 |

1,000 条数据中每类问题各有 250 条，记录包含问题、参考答案、题型以及生成和验证模型信息。`data/逐题审核明细.md` 保存 100 条 QA 的审核记录与候选修订答案。

## 生成 QA 数据

通过 OpenAI-compatible `/chat/completions` 接口，根据运行时 RAG 文档生成问题与参考答案。

```powershell
$env:QA_API_KEY = "your-api-key"
python scripts/generate_qa.py --count 20
```

| 参数 | 环境变量 | 默认值或要求 |
| --- | --- | --- |
| `--api-key` | `QA_API_KEY` | 必填 |
| `--api-base` | `QA_API_BASE` | `https://api.siliconflow.cn/v1` |
| `--api-model` | `QA_API_MODEL` | `deepseek-ai/DeepSeek-V3.1-Terminus` |
| `--count` | - | 生成尝试次数，默认 20 |

生成的 `qa_dataset.jsonl` 与 `qa_generation_report.md` 保存在 `reports/qa_generation/<timestamp>/` 下。

## 离线校验

```powershell
python -m unittest discover -s tests -p test_offline.py -v
```

校验内容包括知识库加载、索引清单、QA 数据格式、模型目录命名与预测脚本入口。

## 后续发布计划

我们计划在后续更新中发布 EGMAR 与 TextStarCraft II 的适配和集成代码。
