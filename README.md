# StarCraft RAG（本地 Qwen3-8B + BGE-M3）

一个可直接上传 Git 的星际争霸 II 知识库问答项目。它保留 RAG 检索、智能体推理与答案综合的完整本地流程，移除了 baseline、baseline 评估以及最终问题预测的评分流程。

## 功能与边界

- 默认完整流程：**本地 Qwen3-8B 路由 → BGE-M3 混合检索 → 本地 LLM 智能体证据推理 → 本地 LLM 答案综合**。
- 批量流程只保存每个问题的最终预测答案，不读取参考答案、不计算 F1、不输出 PASS/FAIL。
- 运行问答和批量预测不调用任何 LLM API；智能体、路由器和答案综合均使用本地模型。
- 仅“问题生成”使用 OpenAI-compatible API，且 API Key 必须由命令行参数或环境变量提供，项目中不保存密钥。
- 内置运行时知识库、预构建 BGE 索引和 20 条 QA 问题数据；模型权重不纳入 Git。

## 目录

```text
starcraft-rag/
├── data/
│   ├── runtime_kb/       # RAG 知识库与预构建 BGE 索引
│   └── qa/               # 内置 20 条问题数据
├── scripts/
│   ├── query.py          # 单问题问答
│   ├── predict_qa.py     # 批量本地预测，只保存最终答案
│   └── generate_qa.py    # API 问题生成，输出数据集与 Markdown 报告
├── src/starcraft_rag/    # RAG、检索器、智能体和本地 LLM 实现
├── reports/              # 预测或问题生成结果（Git 忽略）
├── tests/                # 无模型离线校验
└── requirements.txt
```

## 安装

建议使用 Python 3.10 或更高版本，并根据本机 CUDA/CPU 环境安装兼容的 PyTorch：

```powershell
cd D:\StarCraft\LLM-PySC2-master\K-LLMA\starcraft-rag
python -m pip install -r requirements.txt
```

## 模型路径参数：`--model-root`

唯一需要为本地推理调整的参数是 `--model-root`。该目录下必须包含：

```text
<model-root>/
├── Qwen3-8B/
└── bge-m3/
```

默认值是仓库同级原项目中的 `my_knowledge\starcraft_rag\LLM`，即：

```text
D:\StarCraft\LLM-PySC2-master\my_knowledge\starcraft_rag\LLM
```

因此在当前工作区无需传参；在其他机器上可显式指定模型目录，或设置环境变量 `SC2_MODEL_ROOT`。

```powershell
python scripts\query.py "How do I counter Dark Templar?" --model-root E:\models\starcraft_llm
```

## 本地问答与批量预测

单问题问答：

```powershell
python scripts\query.py "How do I counter Dark Templar?"
```

运行完整 20 条问题预测流程（默认 BGE、本地 Qwen、智能体和本地答案综合全部启用）：

```powershell
python scripts\predict_qa.py
```

可选参数只有：

- `--model-root <目录>`：替换本地 Qwen3-8B 与 BGE-M3 的共同父目录。
- `--questions <jsonl>`：替换输入问题文件；其中的参考答案字段不会被读取。
- `--limit <N>`：只预测前 N 条，用于快速排查。

每次运行都会创建 `reports/predictions/<时间戳>/prediction_results.md` 与 `predictions.json`。两者仅含问题、预测答案和运行错误信息，不含参考答案、评分、F1 或 PASS/FAIL。

## 生成 QA（唯一使用 API 的流程）

问题生成需要显式给出 API Key；密钥不会写入报告、数据集或 Git。支持任意 OpenAI-compatible `/chat/completions` 接口：

```powershell
python scripts\generate_qa.py --api-key $env:QA_API_KEY --count 20
```

也可以通过环境变量提供 `QA_API_KEY`，再直接运行：

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

## Git 上传说明

- 可直接上传源代码、`data/runtime_kb`、预构建索引及内置问题数据。
- 请不要上传 Qwen3-8B、BGE-M3 权重、API Key、`.env` 与运行结果；它们已在 `.gitignore` 中处理。
- 本项目不包含 baseline 代码、baseline 索引、baseline 评估或问题预测评估流程。

---

**版本说明：当前为 Qwen3-8B 基础版本。本仓库提供论文实验所需的最小可复现实现与运行说明；论文录用后，我们计划进一步完善，并可能发布更完整的工程版本。**
