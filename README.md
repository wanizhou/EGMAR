# StarCraft RAG（本地 Qwen3-8B + BGE-M3）

一个面向星际争霸 II 知识问答的本地 RAG 项目，包含检索、智能体推理、答案综合、批量预测与 QA 数据生成流程。

## 功能与边界

- 默认完整流程：**本地 Qwen3-8B 路由 → BGE-M3 混合检索 → 本地 LLM 智能体证据推理 → 本地 LLM 答案综合**。
- 提供单问题问答与批量预测，预测结果以 Markdown 和 JSON 格式保存。
- 提供运行时知识库、预构建 BGE-M3 索引，以及 20 条快速验证数据和 1000 条批量 QA 数据。
- 提供基于 OpenAI-compatible 接口的 QA 数据生成脚本。

## 目录

```text
starcraft-rag/
├── data/
│   ├── runtime_kb/       # RAG 知识库与预构建 BGE 索引
│   └── qa/               # 20 条快速验证数据与 1000 条批量 QA 数据
├── scripts/
│   ├── query.py          # 单问题问答
│   ├── predict_qa.py     # 批量本地预测
│   └── generate_qa.py    # API 问题生成，输出数据集与 Markdown 报告
├── src/starcraft_rag/    # RAG、检索器、智能体和本地 LLM 实现
├── reports/              # 预测或问题生成结果（Git 忽略）
├── tests/                # 无模型离线校验
└── requirements.txt
```

## 安装

建议使用 Python 3.10 或更高版本，并根据本机 CUDA/CPU 环境安装兼容的 PyTorch：

```powershell
git clone https://github.com/<owner>/K-LLMA.git
cd K-LLMA
python -m pip install -r requirements.txt
```

## 模型路径参数：`--model-root`

唯一需要为本地推理调整的参数是 `--model-root`。该目录下必须包含：

```text
<model-root>/
├── Qwen3-8B/
└── bge-m3/
```

模型根目录可通过 `--model-root` 指定，也可通过环境变量 `SC2_MODEL_ROOT` 配置。

```powershell
python scripts\query.py "How do I counter Dark Templar?" --model-root E:\models\starcraft_llm
```

## 问答与批量预测

单问题问答：

```powershell
python scripts\query.py "How do I counter Dark Templar?"
```

使用 20 条快速验证数据运行批量预测：

```powershell
python scripts\predict_qa.py --questions data\qa\qa_dataset_20.jsonl
```

使用 1000 条 QA 数据运行批量预测：

```powershell
python scripts\predict_qa.py --questions data\qa\qa_dataset_1000.jsonl
```

常用参数：

- `--model-root <目录>`：替换本地 Qwen3-8B 与 BGE-M3 的共同父目录。
- `--questions <jsonl>`：指定输入问题文件。
- `--limit <N>`：限制本次预测的问题数量。

每次运行都会创建 `reports/predictions/<时间戳>/prediction_results.md` 与 `predictions.json`，记录问题与对应预测结果。

## 生成 QA 数据

QA 数据生成支持 OpenAI-compatible `/chat/completions` 接口：

```powershell
python scripts\generate_qa.py --api-key $env:QA_API_KEY --count 20
```

也可以通过环境变量 `QA_API_KEY` 配置访问凭据：

```powershell
$env:QA_API_KEY = "your-key"
python scripts\generate_qa.py --count 20
```

API 相关参数：

- `--api-key`：必填；也可使用 `QA_API_KEY` 环境变量。
- `--api-base`：API 根地址，默认 `https://api.siliconflow.cn/v1`；也可使用 `QA_API_BASE`。
- `--api-model`：生成模型名；也可使用 `QA_API_MODEL`。
- `--count`：生成数量，默认 20。

生成完成后会写入 `reports/qa_generation/<时间戳>/qa_dataset.jsonl` 和 `qa_generation_report.md`。

## 校验

不加载模型的结构和数据校验：

```powershell
python -m unittest tests\test_offline.py
```

---

**版本说明：当前为 Qwen3-8B 基础版本。本仓库提供论文实验所需的最小可复现实现与运行说明；论文录用后，我们计划进一步完善，并可能发布更完整的工程版本。**
